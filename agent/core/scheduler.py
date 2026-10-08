"""
Scheduled tasks — one-shot and recurring jobs.
"""

import os
import json
import time
import threading
import subprocess

SCHEDULE_FILE = os.path.expanduser("~/.kibo_schedule.json")
_jobs = []
_jobs_lock = threading.Lock()
_scheduler_thread = None
_scheduler_running = False


def _load_jobs():
    """Load jobs from disk."""
    global _jobs
    if os.path.exists(SCHEDULE_FILE):
        with open(SCHEDULE_FILE) as f:
            _jobs = json.load(f)


def _save_jobs():
    """Save jobs to disk."""
    with open(SCHEDULE_FILE, "w") as f:
        json.dump(_jobs, f, indent=2)


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
        job = {
            "id": len(_jobs) + 1,
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
        status = "ACTIVE" if j["active"] else "PAUSED"
        repeat = f"every {j['repeat']}s" if j["repeat"] else "one-shot"
        result += f"  #{j['id']} [{status}] {j['label']} ({repeat})\n"
        result += f"       Runs: {j['run_count']}, Next: "
        if j["next_run"]:
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


def _scheduler_loop():
    """Main scheduler loop."""
    global _scheduler_running
    while _scheduler_running:
        time.sleep(1)
        now = time.time()

        with _jobs_lock:
            _load_jobs()
            for job in _jobs:
                if not job["active"]:
                    continue
                if job["next_run"] and now >= job["next_run"]:

           
                    _run_job(job)
                    job["last_run"] = now
                    job["run_count"] += 1

           
                    if job["repeat"] > 0:
                        job["next_run"] = now + job["repeat"]
                    else:
                        job["active"] = False
                        job["next_run"] = None

            _save_jobs()


def _start_scheduler():
    """Start the scheduler thread if not running."""
    global _scheduler_thread, _scheduler_running
    if _scheduler_running:
        return
    _scheduler_running = True
    _scheduler_thread = threading.Thread(target=_scheduler_loop, daemon=True)
    _scheduler_thread.start()
