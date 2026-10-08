"""
Desktop widget tool — set/clear custom messages shown in the top bar widget.
"""

import needle


def _set_msg(message, animation="fade"):
    from agent.core.agent_state import set_widget_message, clear_widget_message
    if not message or message.strip() == "":
        clear_widget_message()
        return False
    set_widget_message(message.strip(), animation)
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



@needle.tool
def pet_show(text: str) -> str:
    """Show a message on the desktop pet widget with a smooth fade animation.
    Use when the user says 'pet show <text>'. The text stays visible
    while idle, hides while Kibo is working, and reappears when done."""
    print(f"[Tool] pet_show('{text}')")
    if not _set_msg(text, "fade"):
        return "Pet message cleared."
    return f"Pet widget shows: {text.strip()}"


@needle.tool
def pet_send(text: str) -> str:
    """Send a message to the desktop pet widget with a typewriter animation.
    Use when the user says 'pet send <text>'. The text stays visible
    while idle, hides while Kibo is working, and reappears when done."""
    print(f"[Tool] pet_send('{text}')")
    if not _set_msg(text, "type"):
        return "Pet message cleared."
    return f"Pet widget typed: {text.strip()}"


@needle.tool
def pet_love(text: str = "I love you") -> str:
    """Show an affectionate message on the desktop pet widget with a
    hearts bounce animation. Use when the user says 'pet i love you'
    or wants a heart-style message. Text stays visible while idle."""
    print(f"[Tool] pet_love('{text}')")
    if not _set_msg(text, "hearts"):
        return "Pet message cleared."
    return f"Pet widget hearts: {text.strip()}"


@needle.tool
def pet_clear() -> str:
    """Clear the message from the desktop pet widget."""
    print("[Tool] pet_clear()")
    from agent.core.agent_state import clear_widget_message
    clear_widget_message()
    return "Pet widget message cleared."



@needle.tool
def pet_animate(action: str) -> str:
    """Play a one-shot animation on the desktop pet widget.
    Use when the user wants to make the pet move or emote.
    Actions: celebrate, dance, party, love, hearts, happy, sleepy,
    yawn, working, busy, pixel, mochi, reset, sparkle, twinkle,
    fireworks, boom, orbit, heartrain, shower, music, sing,
    rainbow, giggle, laugh, zoomies, dash.
    Example: 'dance with kibo', 'make the pet sleep',
    'pet celebrates', 'fireworks please', 'sing a song'."""
    print(f"[Tool] pet_animate('{action}')")
    if not action or not action.strip():
        return "No action given."
    from agent.core.agent_state import set_pet_action
    set_pet_action(action.strip().lower())
    return f"Pet animation: {action.strip()}"
