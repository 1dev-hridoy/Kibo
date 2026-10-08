import needle




@needle.tool
def reminders_on() -> str:
    """Turn on automatic health reminders (water, eyes, stretch, posture,
    grass). They pop up on the pet widget on a healthy schedule, paused
    overnight (11pm-7am). Use when the user wants automatic reminders."""
    print("[Tool] reminders_on()")
    from agent.runner.reminders import set_enabled, ensure_jobs
    set_enabled(True)
    ensure_jobs()
    return "Automatic reminders ON: water 45m, eyes 30m, stretch 60m, posture 90m, grass 3h."





@needle.tool
def reminders_off() -> str:
    """Turn off automatic health reminders. Use when the user wants to
    stop the automatic water/eyes/stretch/posture/grass reminders."""
    print("[Tool] reminders_off()")
    from agent.runner.reminders import set_enabled
    from agent.core.scheduler import _load_jobs, _save_jobs
    set_enabled(False)
    _load_jobs()
    from agent.core import scheduler as _sched
    _sched._jobs = [j for j in _sched._jobs
                    if not j.get("label", "").startswith("reminder:")]
    _save_jobs()
    return "Automatic reminders OFF."




@needle.tool
def reminders_status() -> str:
    """Show whether automatic health reminders are on and their schedule."""
    print("[Tool] reminders_status()")
    from agent.runner.reminders import is_enabled
    from agent.core.scheduler import list_tasks
    state = "ON" if is_enabled() else "OFF"
    return f"Automatic reminders: {state}\n{list_tasks()}"
