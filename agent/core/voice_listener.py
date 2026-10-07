"""
Voice listener daemon — background thread that listens for wake word
and routes commands through the agent pipeline.
"""

import threading
import time

from agent.runner.voice import listen_continuous
from agent.runner.notifications import speak, notify


_listener_thread: threading.Thread | None = None
_stop_event = threading.Event()
_is_running = False
_command_callback = None


def _default_command_handler(command: str):
    """Default handler: process command through ask() and speak the response."""
    try:
        from agent.core.ask import ask
        response = ask(command)
        if response:
            speak(str(response))
    except Exception as e:
        notify("Voice Error", str(e))


def start_listener(wake_word: str = "hey kibo",
                   command_handler=None) -> str:
    """Start the wake-word listener in a background thread.

    Args:
        wake_word: The phrase to trigger listening.
        command_handler: Callable that receives the command string.
                        Defaults to processing through ask() + TTS.

    Returns status message.
    """
    global _listener_thread, _is_running, _command_callback, _stop_event

    if _is_running:
        return "Voice listener is already running."

    _stop_event.clear()
    _command_callback = command_handler or _default_command_handler
    _is_running = True

    def _listener_loop():
        global _is_running
        try:
            listen_continuous(
                callback=_command_callback,
                stop_event=_stop_event,
                wake_word=wake_word,
            )
        finally:
            _is_running = False

    _listener_thread = threading.Thread(target=_listener_loop, daemon=True)
    _listener_thread.start()

    return f"Voice listener started (wake word: '{wake_word}')"


def stop_listener() -> str:
    """Stop the wake-word listener."""
    global _is_running
    if not _is_running:
        return "Voice listener is not running."

    _stop_event.set()
    _is_running = False
    return "Voice listener stopped."


def get_listener_status() -> dict:
    """Get the current state of the voice listener."""
    return {
        "running": _is_running,
        "has_thread": _listener_thread is not None and _listener_thread.is_alive(),
    }


def voice_command_once(timeout: float = 10.0) -> str:
    """Listen for a single voice command (no wake word required).

    Args:
        timeout: Max seconds to listen.

    Returns the transcribed text.
    """
    from agent.runner.voice import listen_once
    return listen_once(timeout=timeout)


def process_voice_command(command: str) -> str:
    """Process a voice command through the agent and return the response.

    Args:
        command: The transcribed voice command.

    Returns the agent's text response.
    """
    try:
        from agent.core.ask import ask
        return str(ask(command))
    except Exception as e:
        return f"Error processing command: {e}"
