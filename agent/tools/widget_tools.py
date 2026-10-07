"""
Desktop widget tool — set/clear custom messages shown in the top bar widget.
"""

import needle


def _set_msg(message):
    from agent.core.agent_state import set_widget_message, clear_widget_message
    if not message or message.strip() == "":
        clear_widget_message()
        return False
    set_widget_message(message.strip())
    return True


def _clear_msg():
    from agent.core.agent_state import clear_widget_message
    clear_widget_message()


@needle.tool
def widget_set_message(message: str, state: str = "idle") -> str:
    """Show a custom message in the desktop widget bar at the top of the screen.
    The widget expands from a small avatar pill to show your message.
    State: 'idle' (green), 'working' (yellow), or 'approval' (red).
    Auto-clears when idle or when called with an empty string.
    Use for: showing status, greetings, reminders, task progress."""
    print(f"[Tool] widget_set_message('{message}', '{state}')")
    if not _set_msg(message):
        return "Widget message cleared."
    return f"Widget message set: {message.strip()}"


@needle.tool
def widget_clear() -> str:
    """Clear the custom message from the desktop widget (back to idle pill)."""
    print("[Tool] widget_clear()")
    _clear_msg()
    return "Widget message cleared."
