import os
import json

from agent.core.scheduler import (schedule_task, find_tasks,
                                  _start_scheduler)

STATE_FILE = os.path.expanduser("~/.config/kibo/reminders.json")

DEFAULTS = {
    "remind_water": {"every": 45 * 60, "delay": 10 * 60},
    "remind_eyes": {"every": 30 * 60, "delay": 20 * 60},
    "remind_stretch": {"every": 60 * 60, "delay": 30 * 60},
    "remind_posture": {"every": 90 * 60, "delay": 45 * 60},
    "remind_grass": {"every": 180 * 60, "delay": 60 * 60},
}


def _load_state():
    try:
        with open(STATE_FILE) as f:
            return json.load(f)
    except (OSError, ValueError):
        return {"enabled": True}


def _save_state(state):
    try:
        os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
        with open(STATE_FILE, "w") as f:
            json.dump(state, f, indent=2)
    except OSError:
        pass


def is_enabled():
    return _load_state().get("enabled", True)


def set_enabled(on: bool):
    state = _load_state()
    state["enabled"] = bool(on)
    _save_state(state)


def ensure_jobs():
    if not is_enabled():
        return "reminders off"
    for name, spec in DEFAULTS.items():
        if not find_tasks(command=f"reminder:{name}"):
            schedule_task(f"reminder:{name}",
                          delay_seconds=spec["delay"],
                          repeat_seconds=spec["every"],
                          label=f"reminder:{name}")
    _start_scheduler()
    return "reminder jobs ensured"
