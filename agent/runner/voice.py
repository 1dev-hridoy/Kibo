"""
Voice pipeline — STT via Vosk, model management, voice command processing.
"""

import json
import os
import queue
import shutil
import struct
import subprocess
import sys
import tempfile
import threading
import wave

from agent.config import IS_LINUX, IS_MACOS, IS_WINDOWS


_MODEL_DIR = os.path.expanduser("~/.config/kibo/vosk_models")
_MODEL_NAME = "vosk-model-small-en-us-0.15"
_MODEL_URL = f"https://alphacephei.com/vosk/models/{_MODEL_NAME}.zip"

_vosk = None
_model = None
_model_lock = threading.Lock()


def _ensure_model() -> str:
    """Download the Vosk model if not present. Returns model directory path."""
    model_path = os.path.join(_MODEL_DIR, _MODEL_NAME)
    if os.path.isdir(model_path):
        return model_path

    os.makedirs(_MODEL_DIR, exist_ok=True)
    zip_path = os.path.join(_MODEL_DIR, f"{_MODEL_NAME}.zip")

    print(f"[Voice] Downloading Vosk model (~50MB)...")
    try:
        import urllib.request
        urllib.request.urlretrieve(_MODEL_URL, zip_path)
    except Exception as e:
        raise RuntimeError(f"Failed to download Vosk model: {e}")

    
    import zipfile
    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(_MODEL_DIR)
    os.remove(zip_path)
    print(f"[Voice] Model installed to {model_path}")
    return model_path


def _get_model():
    """Get or initialize the Vosk model (lazy, thread-safe)."""
    global _vosk, _model
    if _model is not None:
        return _model

    with _model_lock:
        if _model is not None:
            return _model

        try:
            import vosk
        except ImportError:
            raise RuntimeError("vosk not installed — run: pip install vosk")

        _vosk = vosk
        vosk.SetLogLevel(-1)

        model_path = _ensure_model()
        _model = vosk.KaldiRecognizer(vosk.Model(model_path), 16000)
        return _model


def _find_mic_recorder():
    """Find a CLI tool that can record raw 16kHz mono audio to stdout."""
    if IS_LINUX:
        for name in ["parecord", "pw-record", "arecord"]:
            path = shutil.which(name)
            if path:
                return path, name
    if IS_MACOS:
        path = shutil.which("ffmpeg")
        if path:
            return path, "ffmpeg-mac"
    if IS_WINDOWS:
        path = shutil.which("ffmpeg")
        if path:
            return path, "ffmpeg-win"
    return None, None


def _find_default_source():
    """Find the default PulseWire/PulseAudio input device name."""
    try:
        r = subprocess.run(
            ["pactl", "list", "sources", "short"],
            capture_output=True, text=True, timeout=5, errors="replace")
        for line in r.stdout.splitlines():
            parts = line.split()
            if len(parts) >= 2 and "input" in parts[1].lower():
                return parts[1]
    except Exception:
        pass
    
    try:
        r = subprocess.run(
            ["pw-cli", "ls", "Node"],
            capture_output=True, text=True, timeout=5, errors="replace")
        for line in r.stdout.splitlines():
            if "Audio/Source" in line:
         
                pass
    except Exception:
        pass
    return None


def listen_once(timeout: float = 10.0) -> str:
    """Record audio from the mic and transcribe it using Vosk.

    Args:
        timeout: Max seconds to listen.

    Returns transcribed text, or empty string if nothing heard.
    """
    model = _get_model()
    rec_path, rec_name = _find_mic_recorder()
    if not rec_path:
        print("[Voice] No microphone recorder found.")
        return ""


    source_device = _find_default_source() if IS_LINUX else None
    print(f"[Voice] Recording with {rec_name} (device: {source_device}) for {timeout}s...")

   
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        tmp_path = tmp.name

    try:
        kwargs = {}
        if IS_WINDOWS:
            kwargs["creationflags"] = 0x08000000  

        if rec_name == "parecord":
            cmd = [rec_path, "--format=s16le", "--rate=16000",
                   "--channels=1"]
            if source_device:
                cmd.extend(["--device", source_device])
            cmd.append(tmp_path)
        elif rec_name == "pw-record":
            cmd = [rec_path, "--format", "s16", "--rate", "16000",
                   "--channels", "1"]
            if source_device:
                cmd.extend(["--target", source_device])
            cmd.append(tmp_path)
        elif rec_name == "arecord":
            cmd = [rec_path, "-f", "S16_LE", "-r", "16000", "-c", "1",
                   tmp_path]
        elif rec_name == "ffmpeg-mac":
            cmd = [rec_path, "-y", "-f", "avfoundation", "-i", ":0",
                   "-ar", "16000", "-ac", "1", "-f", "s16le", tmp_path]
        elif rec_name == "ffmpeg-win":
            cmd = [rec_path, "-y", "-f", "dshow", "-i",
                   "audio=Default Input", "-ar", "16000", "-ac", "1",
                   "-f", "s16le", tmp_path]
        else:
            return ""

        proc = subprocess.Popen(
            cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            **kwargs)


        try:
            proc.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            proc.terminate()
            proc.wait(timeout=2)

     
        if not os.path.exists(tmp_path) or os.path.getsize(tmp_path) < 100:
            print(f"[Voice] Recording empty (no audio captured).")
            return ""

        print(f"[Voice] Recorded {os.path.getsize(tmp_path)} bytes, transcribing...")

        with wave.open(tmp_path, "rb") as wf:
            if wf.getframerate() != 16000:
                return ""
            chunk_size = 4000
            while True:
                data = wf.readframes(chunk_size)
                if len(data) == 0:
                    break
                model.AcceptWaveform(data)

            result = json.loads(model.FinalResult())
            text = result.get("text", "").strip()
            print(f"[Voice] Transcribed: '{text}'")
            return text

    finally:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass


def listen_continuous(callback, stop_event: threading.Event | None = None,
                      wake_word: str = "hey kibo"):
    """Continuously listen for a wake word, then capture a command.

    Args:
        callback: Called with the transcribed command text when ready.
        stop_event: Threading event to stop listening.
        wake_word: The phrase to listen for before capturing a command.
    """
    if stop_event is None:
        stop_event = threading.Event()

    model = _get_model()
    rec_path, rec_name = _find_mic_recorder()
    if not rec_path:
        print("[Voice] No microphone recorder found.")
        return

    source_device = _find_default_source() if IS_LINUX else None


    if rec_name == "parecord":
        cmd = [rec_path, "--format=s16le", "--rate=16000",
               "--channels=1"]
        if source_device:
            cmd.extend(["--device", source_device])
        cmd.append("-")
    elif rec_name == "pw-record":
        cmd = [rec_path, "--format", "s16", "--rate", "16000",
               "--channels", "1"]
        if source_device:
            cmd.extend(["--target", source_device])
        cmd.append("-")
    elif rec_name == "arecord":
        cmd = [rec_path, "-f", "S16_LE", "-r", "16000", "-c", "1", "-"]
    elif rec_name == "ffmpeg-mac":
        cmd = [rec_path, "-f", "avfoundation", "-i", ":0",
               "-ar", "16000", "-ac", "1", "-f", "s16le", "-"]
    elif rec_name == "ffmpeg-win":
        cmd = [rec_path, "-f", "dshow", "-i", "audio=Default Input",
               "-ar", "16000", "-ac", "1", "-f", "s16le", "-"]
    else:
        return

    print(f"[Voice] Listening for wake word '{wake_word}'...")

    kwargs = {}
    if IS_WINDOWS:
        kwargs["creationflags"] = 0x08000000

    try:
        proc = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
            bufsize=1024 * 1024, **kwargs)
    except Exception as e:
        print(f"[Voice] Failed to start microphone: {e}")
        return

    wake_lower = wake_word.lower()
    buffer = b""

    try:
        while not stop_event.is_set():
            chunk = proc.stdout.read(4096)
            if not chunk:
                break

            buffer += chunk
      
            while len(buffer) >= 8000:
                pcm_data = buffer[:8000]
                buffer = buffer[8000:]

                if model.AcceptWaveform(pcm_data):
                    result = json.loads(model.Result())
                    text = result.get("text", "").lower().strip()

                    if wake_lower in text:
                        print(f"[Voice] Wake word detected! Listening for command...")
                  
                        command = _capture_command(model, proc, stop_event, timeout=8.0)
                        if command:
                            print(f"[Voice] Command: {command}")
                            callback(command)

         
            partial = json.loads(model.PartialResult())
            partial_text = partial.get("partial", "").lower().strip()
            if wake_lower in partial_text:
                print(f"[Voice] Wake word (partial) detected!")
                command = _capture_command(model, proc, stop_event, timeout=8.0)
                if command:
                    print(f"[Voice] Command: {command}")
                    callback(command)

    except Exception as e:
        print(f"[Voice] Listener error: {e}")
    finally:
        try:
            proc.terminate()
            proc.wait(timeout=2)
        except Exception:
            pass


def _capture_command(model, proc, stop_event, timeout: float = 8.0) -> str:
    """After wake word, listen for a command for a fixed duration."""
    import time
    start = time.time()
    buffer = b""

    while time.time() - start < timeout and not stop_event.is_set():
        chunk = proc.stdout.read(4096)
        if not chunk:
            break
        buffer += chunk

        while len(buffer) >= 8000:
            pcm_data = buffer[:8000]
            buffer = buffer[8000:]
            model.AcceptWaveform(pcm_data)

    result = json.loads(model.FinalResult())
    return result.get("text", "").strip()
