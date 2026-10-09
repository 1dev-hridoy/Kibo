"""
Scheduled tasks — one-shot and recurring jobs.
"""

import os
import json
import time
import threading
import subprocess

try:
    import fcntl
except ImportError:          # Windows — thread lock only
    fcntl = None

SCHEDULE_FILE = os.path.expanduser("~/.kibo_schedule.json")
LOCK_FILE = SCHEDULE_FILE + ".lock"
_jobs = []
_jobs_lock = threading.Lock()
_scheduler_thread = None
_scheduler_running = False
_lock_fh = None



MISSED_GRACE = 1200


def _read_jobs():
    """Read jobs from disk without touching the module-level list."""
    try:
        with open(SCHEDULE_FILE) as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except (OSError, ValueError):
        return []







def _write_jobs(jobs):
    """Atomically replace the schedule file."""
    try:
        tmp = SCHEDULE_FILE + ".tmp"
        with open(tmp, "w") as f:
            json.dump(jobs, f, indent=2)
        os.replace(tmp, SCHEDULE_FILE)
    except OSError:
        pass





def _acquire():
    """Take the cross-process scheduler lock.

    False means another Kibo process is running this tick, so we skip it —
    otherwise the web UI, widget, Telegram bot and CLI would each fire the
    same job and each write the schedule back over the others.
    """
    global _lock_fh
    if fcntl is None:
        return True
    if _lock_fh is None:



        try:
            _lock_fh = open(LOCK_FILE, "a+")
        except OSError:
            _lock_fh = None
            return True
    try:



        fcntl.flock(_lock_fh, fcntl.LOCK_EX | fcntl.LOCK_NB)
        return True
    except OSError:
        return False


def _release():
    if fcntl is not None and _lock_fh is not None:
        try:
            fcntl.flock(_lock_fh, fcntl.LOCK_UN)
        except OSError:
            pass


def _load_jobs():
    """Load jobs from disk into the module-level list."""
    global _jobs
    _jobs = _read_jobs()
    return _jobs


def _save_jobs():
    """Persist the module-level list to disk."""
    _write_jobs(_jobs)


def find_tasks(command=None, label=None):
    """Every job matching a command or label (empty list if none)."""
    _load_jobs()
    out = []
    for j in _jobs:
        if command and j.get("command") == command:
            out.append(j)
        elif label and j.get("label") == label:
            out.append(j)
    return out


def schedule_task(command, delay_seconds=0, repeat_seconds=0, label=""):
    """Schedule a task to run.
    
    Args:
        command: Shell command or agent instruction
        delay_seconds: Delay before first run (0 = now)
        repeat_seconds: Repeat interval (0 = one-shot)
        label: Optional label
    """
    with _jobs_lock:
        _load_jobs()
        next_id = max([int(j.get("id", 0)) for j in _jobs] or [0]) + 1
        job = {
            "id": next_id,
            "command": command,
            "delay": delay_seconds,
            "repeat": repeat_seconds,
            "label": label or command[:50],
            "active": True,
            "created": time.time(),
            "last_run": None,
            "run_count": 0,
            "next_run": time.time() + delay_seconds,
        }
        _jobs.append(job)
        _save_jobs()
        _start_scheduler()
        return f"Task #{job['id']} scheduled: {job['label']}"


def cancel_task(task_id):
    """Cancel a scheduled task."""
    with _jobs_lock:
        _load_jobs()
        for i, j in enumerate(_jobs):
            if j["id"] == task_id:
                _jobs.pop(i)
                _save_jobs()
                return f"Task #{task_id} cancelled"
        return f"Task #{task_id} not found"


def list_tasks():
    """List all scheduled tasks."""
    _load_jobs()
    if not _jobs:
        return "No scheduled tasks"

    result = "Scheduled tasks:\n"
    for j in _jobs:
        status = "ACTIVE" if j.get("active") else "PAUSED"
        repeat = f"every {j.get('repeat', 0)}s" if j.get("repeat") else "one-shot"
        result += f"  #{j.get('id')} [{status}] {j.get('label', '')} ({repeat})\n"
        result += f"       Runs: {j.get('run_count', 0)}, Next: "
        if j.get("next_run"):
            remaining = max(0, j["next_run"] - time.time())
            result += f"in {remaining:.0f}s\n"
        else:
            result += "paused\n"
    return result


def pause_task(task_id):
    """Pause a scheduled task."""
    with _jobs_lock:
        _load_jobs()
        for j in _jobs:
            if j["id"] == task_id:
                j["active"] = False
                _save_jobs()
                return f"Task #{task_id} paused"
        return f"Task #{task_id} not found"


def resume_task(task_id):
    """Resume a paused task."""
    with _jobs_lock:
        _load_jobs()
        for j in _jobs:
            if j["id"] == task_id:
                j["active"] = True
                j["next_run"] = time.time() + j["delay"]
                _save_jobs()
                _start_scheduler()
                return f"Task #{task_id} resumed"
        return f"Task #{task_id} not found"


def reschedule_task(command, next_run):
    """Push an existing job's next run to an absolute timestamp.

    Returns True if a matching job was found. Used to re-anchor jobs whose
    stored next_run went stale (e.g. the machine was off at the time).
    """


    with _jobs_lock:
        _load_jobs()
        changed = False
        for j in _jobs:
            if j.get("command") == command and j.get("active"):
                j["next_run"] = next_run
                changed = True
        if changed:
            _save_jobs()
        return changed





def _advance(job, now, missed=False):
    """Move a job's next run forward after it fired (or was missed)."""
    repeat = int(job.get("repeat", 0) or 0)


    
    if repeat <= 0:


        job["active"] = False

        job["next_run"] = None
        return
    nxt = (job.get("next_run") or now) + repeat
    if nxt <= now:          
        nxt = now + repeat       
    job["next_run"] = nxt
    if missed:
        job["missed_count"] = job.get("missed_count", 0) + 1


def _run_job(job):
    """Execute a job."""
    try:

   
        if job["command"].startswith("reminder:"):
            import datetime
            hour = datetime.datetime.now().hour
            if hour >= 23 or hour < 7:
                return
            name = job["command"].split(":", 1)[1]
            from agent.tools import ALL_TOOLS
            
            
            for fn in ALL_TOOLS:


                if fn.__name__ == name:
                    fn()
                    return
            print(f"[Scheduler] Unknown tool '{name}'")
            return

        if job["command"].startswith("briefing:"):
            name = job["command"].split(":", 1)[1]
            if name == "brief_today":
                from agent.tools.briefing_tools import run_scheduled_briefing
                run_scheduled_briefing()
                return
            from agent.tools import ALL_TOOLS
            for fn in ALL_TOOLS:
                if fn.__name__ == name:
                    fn()
                    return
            print(f"[Scheduler] Unknown tool '{name}'")
            return

        if job["command"].startswith("agent:"):
  
            from agent.core.ask import ask
            ask(job["command"][6:])
        else:

   
            subprocess.run(
                job["command"], shell=True,
                capture_output=True, timeout=30
            )
    except Exception as e:
        print(f"[Scheduler] Error running task #{job['id']}: {e}")


def _due_jobs(jobs, now):
    """Split due jobs into (run_now, missed), advancing the missed ones."""
    run_now, missed = [], []
    for job in jobs:
        if not job.get("active"):
            continue
        nxt = job.get("next_run")
        if not nxt or now < nxt:
            continue
        if now - nxt > MISSED_GRACE:
            missed.append(job)
        else:
            run_now.append(job)
    return run_now, missed


def _tick():
    """One scheduler pass.

    Due jobs are claimed — advanced and written to disk — *before* their
    body runs. A job may reload or rewrite the schedule while running (the
    briefing reads the agenda, the reminder tools touch the widget), so
    marking them first is what stops a job from being replayed every second
    and stops a second Kibo process from firing the same job.
    """


    with _jobs_lock:
        if not _acquire():
            return

        


        try:



            jobs = _read_jobs()
            if not jobs:
                return
            now = time.time()
            run_now, missed = _due_jobs(jobs, now)
            for job in run_now:
                job["last_run"] = now
                job["run_count"] = job.get("run_count", 0) + 1
                _advance(job, now)
            for job in missed:
                _advance(job, now, missed=True)
            if run_now or missed:
                _write_jobs(jobs)
            for job in run_now:
                _run_job(job)
        finally:
            _release()



def _scheduler_loop():
    """Main scheduler loop."""
    while _scheduler_running:
        time.sleep(1)
        try:
            _tick()
        except Exception as e:
            print(f"[Scheduler] tick error: {e}")


def _start_scheduler():
    """Start the scheduler thread if not running."""
    global _scheduler_thread, _scheduler_running
    if _scheduler_running:
        return
    _scheduler_running = True
    _scheduler_thread = threading.Thread(target=_scheduler_loop, daemon=True)
    _scheduler_thread.start()
