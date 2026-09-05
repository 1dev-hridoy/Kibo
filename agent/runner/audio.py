"""Audio: volume_info(), set_volume(), _RECORD_STATE, record_audio_start(), record_audio_stop()."""

import os
import re
import shutil
import subprocess
import time

from agent.config import IS_WINDOWS, IS_MACOS, IS_LINUX, AUDIO_SAVE_DIR
from agent.runner.common import run, powershell, _find, CREATE_NO_WINDOW


def volume_info() -> list:
    """Return current audio output volume level(s)."""
    if IS_LINUX and shutil.which("pactl"):
        out = run(["pactl", "get-sink-volume", "@DEFAULT_SINK@"], timeout=5)
        m = re.search(r"left:\s*\d+\s*/\s*(\d+)%", out)
        if m:
            return [{"stream": "music", "volume": int(m.group(1)),
                     "max_volume": 100}]
        return []
    if IS_MACOS:
        out = run(["osascript", "-e", "output volume of (get volume settings)"])
        try:
            return [{"stream": "music", "volume": int(out), "max_volume": 100}]
        except ValueError:
            return []
    if IS_WINDOWS:
        script = '''Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;
public class Vol {
    [DllImport("winmm.dll")] public static extern int waveOutGetVolume(UInt32 h, out UInt32 v);
}
'@
$v = 0
[Vol]::waveOutGetVolume(0, [ref]$v) | Out-Null
$pct = [math]::Round((($v -band 0xFFFF) / 65535) * 100)
Write-Output $pct
'''
        out = powershell(script, timeout=30)
        try:
            return [{"stream": "music", "volume": int(out), "max_volume": 100}]
        except ValueError:
            return []
    return []


def set_volume(stream: str, level: int) -> str:
    """Set output volume (0-100). stream: music/media or mic/call."""
    try:
        pct = max(0, min(100, int(level)))
    except (TypeError, ValueError):
        return f"Error: invalid volume level '{level}'."
    source = stream.lower() in ("mic", "call", "source", "input")
    if IS_LINUX and shutil.which("pactl"):
        target = "@DEFAULT_SOURCE@" if source else "@DEFAULT_SINK@"
        verb = "set-source-volume" if source else "set-sink-volume"
        res = run(["pactl", verb, target, f"{pct}%"])
        return f"Volume set to {pct}%" if not res.startswith("Error") else res
    if IS_MACOS:
        return run(["osascript", "-e", f"set volume output volume {pct}"])
    if IS_WINDOWS:
        if source:
            return "Mic volume is controlled with the Windows sound panel."
        script = f'''Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;
public class Vol2 {{
    [DllImport("winmm.dll")] public static extern int waveOutSetVolume(UInt32 h, UInt32 v);
}}
'@
$v = [UInt32]([math]::Round({pct} / 100 * 65535))
[Vol2]::waveOutSetVolume(0, ($v -bor ($v -shl 16))) | Out-Null
Write-Output 'Success'
'''
        res = powershell(script, timeout=30)
        return f"Volume set to {pct}%" if res == "Success" else res
    return "Volume control is unavailable on this system."


_RECORD_STATE = {"proc": None, "path": ""}


def record_audio_start(file_path: str = "") -> str:
    """Start recording audio from the default microphone."""
    if _RECORD_STATE["proc"]:
        return "Error: recording already in progress."
    dest = os.path.expanduser(file_path) if file_path else os.path.join(
        AUDIO_SAVE_DIR, "recording")
    os.makedirs(os.path.dirname(dest) or ".", exist_ok=True)

    kwargs = {}
    if IS_WINDOWS:
        kwargs["creationflags"] = CREATE_NO_WINDOW

    if IS_LINUX:
        rec = _find("pw-record", "parecord", "sox", "arecord", "rec")
        if not rec:
            return "Recording not started — no audio recorder found."
        base = os.path.basename(rec)
        if base in ("pw-record", "parecord"):
            argv = [rec, "--format", "s16", "--rate", "44100",
                    "--channels", "1", f"{dest}.wav"]
        elif base == "arecord":
            argv = [rec, "-f", "S16_LE", "-r", "44100", "-c", "1",
                    f"{dest}.wav"]
        else:  # sox / rec
            argv = [rec, f"{dest}.wav", "rate", "44100"]
    elif IS_MACOS:
        if shutil.which("ffmpeg"):
            argv = ["ffmpeg", "-y", "-f", "avfoundation", "-i", ":0",
                    f"{dest}.wav"]
        else:
            return "Recording not started — install ffmpeg."
    else:  # windows
        if shutil.which("ffmpeg"):
            argv = ["ffmpeg", "-y", "-f", "dshow", "-i",
                    "audio=Default Input", f"{dest}.wav"]
        else:
            return "Recording not started — install ffmpeg (dshow input)."

    try:
        proc = subprocess.Popen(
            argv, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            start_new_session=not IS_WINDOWS, **kwargs)
        _RECORD_STATE["proc"] = proc
        _RECORD_STATE["path"] = f"{dest}.wav"
        time.sleep(0.6)
        if proc.poll() is not None:
            _RECORD_STATE["proc"] = None
            return ("Error: audio recorder exited immediately "
                    f"(code {proc.returncode}) — no input device available?")
        return f"Recording started -> {_RECORD_STATE['path']}"
    except OSError as e:
        return f"Error: {e}"


def record_audio_stop() -> str:
    """Stop any in-progress recording."""
    proc = _RECORD_STATE.get("proc")
    if not proc:
        return "Error: no recording in progress."
    try:
        proc.terminate()
        proc.wait(timeout=5)
    except (OSError, subprocess.TimeoutExpired):
        try:
            proc.kill()
        except OSError:
            pass
    _RECORD_STATE["proc"] = None
    path = _RECORD_STATE.get("path", "")
    _RECORD_STATE["path"] = ""
    if path and os.path.exists(path):
        if os.path.getsize(path) <= 44:  # WAV header only, no samples
            return ("Recording stopped, but the file contains no audio "
                    "(check that a microphone/input device is available).")
        return f"Recording saved to {path}"
    return "Recording stopped (no audio data was written)."
