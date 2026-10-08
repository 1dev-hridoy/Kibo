"""
Autostart tools — enable/disable Kibo launching when the PC starts.
"""

import needle


@needle.tool
def autostart_enable() -> str:
    """Make Kibo start automatically when the PC boots / user logs in.
    ONLY use when the user explicitly asks about PC boot, startup,
    autostart, or login. NEVER use for briefings, reminders, widgets,
    models, or anything else."""
    from agent.runner.autostart import enable
    print("[Tool] autostart_enable()")
    return enable()


@needle.tool
def autostart_disable() -> str:
    """Stop Kibo from starting automatically at PC boot / login.
    Use when the user asks to remove Kibo from startup programs."""
    from agent.runner.autostart import disable
    print("[Tool] autostart_disable()")
    return disable()


@needle.tool
def autostart_status() -> str:
    """Check whether Kibo is configured to start automatically at PC boot."""
    from agent.runner.autostart import status
    print("[Tool] autostart_status()")
    return status()
