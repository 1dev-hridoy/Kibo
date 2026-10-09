import datetime
import os
import json
import time

import needle

STATE_FILE = os.path.expanduser("~/.config/kibo/briefing.json")
HOUR = 8




STALE_AFTER = 3600




WIDGET_TTL = 120


def _load_state():
    try:
        with open(STATE_FILE) as f:
            return json.load(f)
    except (OSError, ValueError):
        return {"enabled": True, "hour": HOUR}



def _save_state(state):
    try:
        os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
        with open(STATE_FILE, "w") as f:
            json.dump(state, f, indent=2)
    except OSError:
        pass





def _today():
    return datetime.date.today().isoformat()



def _sent_today(state=None):
    """True if today's briefing was already delivered."""
    state = _load_state() if state is None else state
    return state.get("last_sent") == _today()




def _mark_sent():
    state = _load_state()
    state["last_sent"] = _today()
    _save_state(state)


def briefing_state():

    return _load_state()




def _next_run_ts(hour):
    """Absolute timestamp of the next HH:00 slot."""
    now = datetime.datetime.now()
    target = now.replace(hour=hour, minute=0, second=0, microsecond=0)

    if target <= now:
        target += datetime.timedelta(days=1)
    return target.timestamp()


def _next_delay(hour):
    now = datetime.datetime.now()

    target = now.replace(hour=hour, minute=0, second=0, microsecond=0)
    if target <= now:
        target += datetime.timedelta(days=1)
    return max(60, int((target - now).total_seconds()))



def ensure_briefing_job():
    from agent.core.scheduler import (schedule_task, find_tasks,
                                     reschedule_task, _start_scheduler)
    state = _load_state()
    if not state.get("enabled", True):
        return "briefing off"

    hour = state.get("hour", HOUR)
    existing = find_tasks(command="briefing:brief_today")

    if not existing:
        schedule_task("briefing:brief_today",
                      delay_seconds=_next_delay(hour),
                      repeat_seconds=86400, label="briefing:daily")
    elif not _sent_today(state):


        
        for job in existing:
            nxt = job.get("next_run")
            if not nxt or nxt < time.time() - STALE_AFTER:
                reschedule_task("briefing:brief_today", _next_run_ts(hour))

    _start_scheduler()
    return "briefing job ensured"



def _remove_briefing_jobs():



    from agent.core.scheduler import _load_jobs, _save_jobs
    from agent.core import scheduler as _sched

    _load_jobs()
    _sched._jobs = [j for j in _sched._jobs
                    if j.get("label") != "briefing:daily"]
    _save_jobs()




@needle.tool
def brief_today() -> str:
    """Give today's briefing: greeting, weather, battery, disk, busiest
    processes and active reminders. Also shows it on the widget.
    Use when the user says 'brief', 'brief the day', 'daily briefing',
    'morning briefing' or asks what's up today."""


    print("[Tool] brief_today()")


    from agent.runner.briefing import build_briefing
    text = build_briefing()
    _mark_sent()

    try:
        from agent.core.agent_state import set_widget_message
        set_widget_message(text.split("\n")[0][:80], "fade",
                           expires_in=WIDGET_TTL)
    except Exception:
        pass


    try:
        from agent.runner.notifications import notify
        notify("Kibo briefing", text)
    except Exception:
        pass
    return text


def run_scheduled_briefing():
    """Automatic briefing entry point — delivers at most one per day.

    Called by the scheduler, never by the model. Returns the briefing text,
    or None when today's briefing has already been delivered.
    """
    if _sent_today():
        print("[Tool] brief_today() already delivered today — skipping")
        return None
    text = brief_today()

    
    _mark_sent()
    return text





@needle.tool
def briefing_on() -> str:
    """Turn on the automatic daily briefing (8am on the widget).
    Use when the user wants a morning briefing every day."""
    print("[Tool] briefing_on()")
    state = _load_state()
    state["enabled"] = True
    _save_state(state)
    ensure_briefing_job()
    return f"Daily briefing ON at {state.get('hour', HOUR)}:00."




@needle.tool
def briefing_off() -> str:
    """Turn off the automatic daily briefing."""
    print("[Tool] briefing_off()")
    state = _load_state()
    state["enabled"] = False
    _save_state(state)
    _remove_briefing_jobs()
    return "Daily briefing OFF."



@needle.tool
def briefing_status() -> str:
    """Show whether the automatic daily briefing is on and when it fires."""
    print("[Tool] briefing_status()")
    from agent.core.scheduler import list_tasks
    state = _load_state()
    on = "ON" if state.get("enabled", True) else "OFF"
    return f"Daily briefing: {on} at {state.get('hour', HOUR)}:00\n{list_tasks()}"
