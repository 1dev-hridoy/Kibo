"""
Alert and schedule tools.
Uses lazy imports to avoid circular dependency with agent.core.
"""


def _import_alerts():
    from agent.core.alerts import (
        add_alert, remove_alert, list_alerts, pause_alert, resume_alert, check_alerts,
    )
    return {
        "add_alert": add_alert, "remove_alert": remove_alert, "list_alerts": list_alerts,
        "pause_alert": pause_alert, "resume_alert": resume_alert, "check_alerts": check_alerts,
    }


def _import_scheduler():
    from agent.core.scheduler import (
        schedule_task, cancel_task, list_tasks, pause_task, resume_task,
    )
    return {
        "schedule_task": schedule_task, "cancel_task": cancel_task, "list_tasks": list_tasks,
        "pause_task": pause_task, "resume_task": resume_task,
    }


def check_system_alerts():
    """Check for triggered alerts and return notifications."""
    alerts = _import_alerts()
    triggered = alerts["check_alerts"]()
    if triggered:
        return "\n".join([
            f"Alert: {t['label']} ({t['metric']}={t['value']:.1f})"
            for t in triggered
        ])
    return "No alerts triggered"


def get_alert_summary():
    """Get a summary of all configured alerts."""
    return _import_alerts()["list_alerts"]()


def schedule_agent_task(instruction, delay=0, repeat=0):
    """Schedule an agent instruction to run later.
    
    Args:
        instruction: What the agent should do
        delay: Seconds to wait before first run
        repeat: Seconds between repeats (0 = one-shot)
    """
    return _import_scheduler()["schedule_task"](f"agent:{instruction}", delay, repeat, instruction[:50])


def schedule_shell_task(command, delay=0, repeat=0):
    """Schedule a shell command to run later.
    
    Args:
        command: Shell command to execute
        delay: Seconds to wait before first run
        repeat: Seconds between repeats (0 = one-shot)
    """
    return _import_scheduler()["schedule_task"](command, delay, repeat, command[:50])
