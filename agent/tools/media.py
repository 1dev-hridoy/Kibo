"""
Media tools — cross-platform: webcam capture (ffmpeg: v4l2/dshow/
avfoundation), audio recording (pw-record/parecord/sox/arecord or
ffmpeg), text-to-speech (espeak-ng / SAPI / say).
"""

import needle
from agent.runner import (
    speak as _speak,
    camera_photo as _camera_photo,
    record_audio_start as _rec_start,
    record_audio_stop as _rec_stop,
)


@needle.tool
def take_camera_photo():
    """Capture a webcam photo and save it to your Downloads folder."""
    print("[Tool] take_camera_photo()")
    return _camera_photo()


@needle.tool
def text_to_speech(text: str):
    """Speak text aloud using the system speech synthesizer."""
    print(f"[Tool] text_to_speech('{text}')")
    try:
        from agent.core.agent_state import set_pet_action
        frames = max(40, min(400, int(len(text or "") * 1.4)))
        set_pet_action(f"talk {frames}")
    except Exception:
        pass
    return _speak(text)


@needle.tool
def record_audio_start(file_path: str = ""):
    """Start recording audio from the microphone."""
    print(f"[Tool] record_audio_start('{file_path}')")
    return _rec_start(file_path)


@needle.tool
def record_audio_stop():
    """Stop the current audio recording."""
    print("[Tool] record_audio_stop()")
    return _rec_stop()
