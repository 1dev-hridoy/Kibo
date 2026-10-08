"""
Voice tool wrappers — wake-word listener, one-shot voice command, voice status.
"""

import needle


def _get_voice_listener():
    """Lazy import to avoid circular dependency."""
    from agent.core.voice_listener import (
        start_listener, stop_listener, get_listener_status,
        process_voice_command,
    )
    return start_listener, stop_listener, get_listener_status, process_voice_command


def _get_listen_once():
    from agent.runner.voice import listen_once
    return listen_once


@needle.tool
def voice_start_listener(wake_word: str = "hey kibo") -> str:
    """Start listening for the wake word in the background.
    When the wake word is heard, Kibo will listen for a command
    and respond with TTS. Runs until voice_stop_listener is called.
    Default wake word is 'hey kibo'. Only change if user explicitly requests a different wake word."""
    print(f"[Tool] voice_start_listener('{wake_word}')")
    start, _, _, _ = _get_voice_listener()
    return start(wake_word)


@needle.tool
def voice_stop_listener() -> str:
    """Stop the background wake-word listener."""
    print("[Tool] voice_stop_listener()")
    _, stop, _, _ = _get_voice_listener()
    return stop()


@needle.tool
def voice_listener_status() -> str:
    """Check if the voice listener is running."""
    print("[Tool] voice_listener_status()")
    _, _, status, _ = _get_voice_listener()
    result = status()
    if result["running"]:
        return "Voice listener is running (wake word active)."
    return "Voice listener is not running."


@needle.tool
def voice_listen_now(duration: int = 10) -> str:
    """Listen for a voice command right now (no wake word needed).
    Speak your command and it will be processed automatically.
    Duration: how many seconds to listen (default 10)."""
    print(f"[Tool] voice_listen_now({duration})")
    duration = max(3, min(30, duration))
    listen_once = _get_listen_once()
    _, _, _, process = _get_voice_listener()
    text = listen_once(timeout=float(duration))
    if not text:
        return "No speech detected. Try speaking closer to the mic."
    return f"Heard: \"{text}\"\n\nProcessing...\n\n{process(text)}"


@needle.tool
def voice_transcribe_only(duration: int = 10) -> str:
    """Listen and transcribe speech to text without processing a command.
    Use for: transcribing notes, dictation, testing mic."""
    print(f"[Tool] voice_transcribe_only({duration})")
    duration = max(3, min(30, duration))
    listen_once = _get_listen_once()
    text = listen_once(timeout=float(duration))
    if not text:
        return "No speech detected."
    return f"Transcription: \"{text}\""
