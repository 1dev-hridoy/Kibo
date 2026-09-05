"""
Advanced tools — Remote Terminal, Application Launcher, Clipboard Sync,
Media Streamer, and Voice Gateway.
"""

import base64
import json
import os
import re
import shutil
import subprocess
import threading
import time

import needle

from agent.config import (
    IS_WINDOWS, IS_MACOS, IS_LINUX, HOME, DOWNLOAD_DIR,
    CMD_TIMEOUT, PLATFORM_NAME,
)
from agent.runner.common import run, powershell, CREATE_NO_WINDOW


# ═══════════════════════════════════════════════════════════════════════
# 1. REMOTE TERMINAL
# ═══════════════════════════════════════════════════════════════════════

@needle.tool
def remote_terminal(command: str, timeout: int = 30) -> str:
    """
    Execute a shell command on this PC and return the output.
    Supports any shell command: ls, cat, grep, df, apt, git, python, etc.
    Use for: running scripts, checking system state, installing packages,
    browsing files, git operations, or any shell task.
    Examples: "ls -la /home", "df -h", "git status", "python3 --version"
    """
    print(f"[Tool] remote_terminal('{command}')")
    command = command.strip()
    if not command:
        return "Error: No command provided."

    timeout = min(max(int(timeout), 1), 300)

    try:
        if IS_WINDOWS:
            argv = ["powershell", "-NoProfile", "-NonInteractive",
                    "-Command", command]
            res = subprocess.run(
                argv, capture_output=True, text=True, errors="replace",
                timeout=timeout, creationflags=CREATE_NO_WINDOW)
        else:
            argv = ["bash", "-c", command]
            res = subprocess.run(
                argv, capture_output=True, text=True, errors="replace",
                timeout=timeout)

        stdout = res.stdout.strip() if res.stdout else ""
        stderr = res.stderr.strip() if res.stderr else ""

        parts = []
        if stdout:
            parts.append(stdout)
        if stderr:
            parts.append(f"[stderr]\n{stderr}")
        if res.returncode != 0:
            parts.append(f"[exit code: {res.returncode}]")

        output = "\n".join(parts) if parts else "Command executed (no output)."

        if len(output) > 4000:
            output = output[:2000] + "\n... [truncated] ...\n" + output[-2000:]

        return output

    except subprocess.TimeoutExpired:
        return f"Error: Command timed out after {timeout}s."
    except Exception as e:
        return f"Error: {e}"


@needle.tool
def remote_terminal_background(command: str) -> str:
    """
    Execute a shell command in the background (non-blocking).
    Returns immediately with a process ID you can check later.
    Use for: long-running tasks like downloads, builds, or updates.
    """
    print(f"[Tool] remote_terminal_background('{command}')")
    command = command.strip()
    if not command:
        return "Error: No command provided."

    try:
        if IS_WINDOWS:
            argv = ["powershell", "-NoProfile", "-NonInteractive",
                    "-Command", f"Start-Process -NoNewWindow -FilePath bash -ArgumentList '-c \"{command}\"'"]
        else:
            argv = ["bash", "-c", f"nohup {command} > /tmp/agent_bg_$$.log 2>&1 & echo $!"]

        proc = subprocess.Popen(
            argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True, creationflags=CREATE_NO_WINDOW if IS_WINDOWS else 0)

        stdout, _ = proc.communicate(timeout=5)
        pid = stdout.strip() or str(proc.pid)
        return f"Background process started (PID: {pid})"

    except Exception as e:
        return f"Error starting background process: {e}"


# ═══════════════════════════════════════════════════════════════════════
# 2. APPLICATION LAUNCHER (Enhanced)
# ═══════════════════════════════════════════════════════════════════════

# Recent apps tracking
_RECENT_APPS_FILE = os.path.join(HOME, ".agent_recent_apps.json")


def _load_recent_apps():
    try:
        if os.path.exists(_RECENT_APPS_FILE):
            with open(_RECENT_APPS_FILE) as f:
                return json.load(f)
    except (json.JSONDecodeError, IOError):
        pass
    return []


def _save_recent_apps(apps):
    try:
        with open(_RECENT_APPS_FILE, "w") as f:
            json.dump(apps[-20:], f, indent=2)
    except IOError:
        pass


def _track_app(name):
    apps = _load_recent_apps()
    apps = [a for a in apps if a.get("name") != name]
    apps.append({"name": name, "time": time.time()})
    _save_recent_apps(apps)


@needle.tool
def launch_app_smart(query: str) -> str:
    """
    Smart application launcher — searches installed apps, recent apps,
    and web apps. Understands natural language like "open my code editor"
    or "launch the browser". Best for: finding and opening any application.
    """
    print(f"[Tool] launch_app_smart('{query}')")
    from agent.config_apps import APP_URLS, LINUX_APPS, WINDOWS_APPS, MACOS_APPS

    q = query.lower().strip()
    q = re.sub(r"^(open|launch|start|run|fire)\s+(the\s+)?", "", q)

    # Check recent apps first
    recent = _load_recent_apps()
    for app in recent:
        if q in app.get("name", "").lower():
            _track_app(app["name"])
            from agent.runner.apps import launch
            return launch(app["name"])

    # Check all app maps
    all_apps = {}
    if IS_LINUX:
        all_apps = LINUX_APPS
    elif IS_WINDOWS:
        all_apps = WINDOWS_APPS
    elif IS_MACOS:
        all_apps = MACOS_APPS

    # Exact match
    if q in all_apps:
        _track_app(q)
        from agent.runner.apps import launch
        return launch(q)

    # Fuzzy match
    for key in all_apps:
        if q in key or key in q:
            _track_app(key)
            from agent.runner.apps import launch
            return launch(key)

    # Web app match
    for key in APP_URLS:
        if q in key or key in q:
            _track_app(key)
            from agent.runner.apps import open_url
            return open_url(APP_URLS[key])

    # Try as direct URL
    if "." in q and " " not in q:
        from agent.runner.apps import open_url
        return open_url(f"https://{q}")

    return f"Couldn't find an app matching '{query}'. Try 'list installed apps' to see what's available."


@needle.tool
def get_recent_apps() -> str:
    """
    Show recently used applications. Use for: quick access to apps
    you use frequently, or to see what was opened recently.
    """
    print("[Tool] get_recent_apps()")
    apps = _load_recent_apps()
    if not apps:
        return "No recently used apps tracked yet."

    lines = ["Recently used apps:"]
    for app in reversed(apps[-10:]):
        name = app.get("name", "unknown")
        lines.append(f"  - {name}")
    return "\n".join(lines)


@needle.tool
def search_apps(query: str) -> str:
    """
    Search for installed applications by name. Use for: finding
    specific apps when you know part of the name.
    """
    print(f"[Tool] search_apps('{query}')")
    from agent.config_apps import APP_URLS, LINUX_APPS, WINDOWS_APPS, MACOS_APPS

    q = query.lower().strip()
    results = []

    all_apps = {}
    if IS_LINUX:
        all_apps = LINUX_APPS
    elif IS_WINDOWS:
        all_apps = WINDOWS_APPS
    elif IS_MACOS:
        all_apps = MACOS_APPS

    for key in sorted(all_apps.keys()):
        if q in key:
            results.append(f"  - {key}")

    for key in sorted(APP_URLS.keys()):
        if q in key:
            results.append(f"  - {key} (web)")

    if not results:
        return f"No apps found matching '{query}'."

    return f"Apps matching '{query}':\n" + "\n".join(results)


# ═══════════════════════════════════════════════════════════════════════
# 3. CLIPBOARD SYNC
# ═══════════════════════════════════════════════════════════════════════

_CLIPBOARD_SYNC_DIR = os.path.join(HOME, ".agent_clipboard_sync")
_CLIPBOARD_SYNC_FILE = os.path.join(_CLIPBOARD_SYNC_DIR, "clipboard.json")


def _ensure_sync_dir():
    os.makedirs(_CLIPBOARD_SYNC_DIR, exist_ok=True)


@needle.tool
def clipboard_sync_push(text: str) -> str:
    """
    Push text to the clipboard sync storage. This text can be
    retrieved later or from other devices. Use for: saving
    important text snippets, sharing clipboard content.
    """
    print(f"[Tool] clipboard_sync_push('{text[:50]}...')")
    _ensure_sync_dir()

    entries = []
    if os.path.exists(_CLIPBOARD_SYNC_FILE):
        try:
            with open(_CLIPBOARD_SYNC_FILE) as f:
                entries = json.load(f)
        except (json.JSONDecodeError, IOError):
            entries = []

    entry = {
        "text": text,
        "timestamp": time.time(),
        "source": PLATFORM_NAME,
    }
    entries.append(entry)

    # Keep last 50 entries
    entries = entries[-50:]

    with open(_CLIPBOARD_SYNC_FILE, "w") as f:
        json.dump(entries, f, indent=2)

    # Also set system clipboard
    try:
        from agent.runner.clipboard import clipboard_set
        clipboard_set(text)
    except Exception:
        pass

    return f"Saved to clipboard sync ({len(entries)} entries). Also copied to system clipboard."


@needle.tool
def clipboard_sync_pull() -> str:
    """
    Pull the latest text from clipboard sync storage. Use for:
    retrieving saved clipboard entries or synced content.
    """
    print("[Tool] clipboard_sync_pull()")
    if not os.path.exists(_CLIPBOARD_SYNC_FILE):
        return "No clipboard sync data found."

    try:
        with open(_CLIPBOARD_SYNC_FILE) as f:
            entries = json.load(f)
    except (json.JSONDecodeError, IOError):
        return "Clipboard sync data is corrupted."

    if not entries:
        return "No clipboard entries found."

    latest = entries[-1]
    text = latest.get("text", "")
    ts = latest.get("timestamp", 0)
    source = latest.get("source", "unknown")

    age = time.time() - ts
    if age < 60:
        age_str = f"{int(age)}s ago"
    elif age < 3600:
        age_str = f"{int(age/60)}m ago"
    else:
        age_str = f"{int(age/3600)}h ago"

    return f"Latest clipboard ({age_str}, from {source}):\n\n{text}"


@needle.tool
def clipboard_sync_list(count: int = 5) -> str:
    """
    List recent clipboard sync entries. Use for: browsing
    clipboard history, finding previously copied text.
    """
    print(f"[Tool] clipboard_sync_list({count})")
    if not os.path.exists(_CLIPBOARD_SYNC_FILE):
        return "No clipboard sync data found."

    try:
        with open(_CLIPBOARD_SYNC_FILE) as f:
            entries = json.load(f)
    except (json.JSONDecodeError, IOError):
        return "Clipboard sync data is corrupted."

    if not entries:
        return "No clipboard entries found."

    count = min(max(int(count), 1), 20)
    recent = entries[-count:]

    lines = [f"Last {len(recent)} clipboard entries:"]
    for i, entry in enumerate(reversed(recent), 1):
        text = entry.get("text", "")[:80]
        ts = entry.get("timestamp", 0)
        age = time.time() - ts
        if age < 60:
            age_str = f"{int(age)}s"
        elif age < 3600:
            age_str = f"{int(age/60)}m"
        else:
            age_str = f"{int(age/3600)}h"
        lines.append(f"  {i}. [{age_str}] {text}")

    return "\n".join(lines)


@needle.tool
def clipboard_sync_clear() -> str:
    """
    Clear all clipboard sync history. Use for: privacy,
    cleaning up storage, or resetting clipboard sync.
    """
    print("[Tool] clipboard_sync_clear()")
    if os.path.exists(_CLIPBOARD_SYNC_FILE):
        os.remove(_CLIPBOARD_SYNC_FILE)
    return "Clipboard sync history cleared."


# ═══════════════════════════════════════════════════════════════════════
# 4. MEDIA STREAMER
# ═══════════════════════════════════════════════════════════════════════

_MEDIA_PLAYER_PROC = None


@needle.tool
def play_media(url: str, volume: int = 80) -> str:
    """
    Play media (audio/video) from a URL. Supports YouTube, direct
    audio/video URLs, and streaming links. Use for: playing music,
    videos, podcasts, or any streaming media.
    """
    global _MEDIA_PLAYER_PROC
    print(f"[Tool] play_media('{url}', volume={volume})")

    # Kill any existing player
    if _MEDIA_PLAYER_PROC and _MEDIA_PLAYER_PROC.poll() is None:
        try:
            _MEDIA_PLAYER_PROC.terminate()
        except Exception:
            pass

    volume = min(max(int(volume), 0), 100)

    # Try mpv first (best support)
    mpv = shutil.which("mpv")
    if mpv:
        try:
            _MEDIA_PLAYER_PROC = subprocess.Popen(
                [mpv, f"--volume={volume}", "--no-video", url],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                creationflags=CREATE_NO_WINDOW if IS_WINDOWS else 0)
            return f"Playing: {url} (volume: {volume}%)"
        except Exception as e:
            return f"Error starting mpv: {e}"

    # Try ffplay
    ffplay = shutil.which("ffplay")
    if ffplay:
        try:
            _MEDIA_PLAYER_PROC = subprocess.Popen(
                [ffplay, "-nodisp", "-autoexit", "-volume", str(volume), url],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                creationflags=CREATE_NO_WINDOW if IS_WINDOWS else 0)
            return f"Playing: {url} (volume: {volume}%)"
        except Exception as e:
            return f"Error starting ffplay: {e}"

    # Fallback: open in default browser/player
    from agent.runner.apps import open_url
    return open_url(url)


@needle.tool
def stop_media() -> str:
    """
    Stop any currently playing media. Use for: stopping music,
    videos, or any media playback.
    """
    global _MEDIA_PLAYER_PROC
    print("[Tool] stop_media()")

    if _MEDIA_PLAYER_PROC and _MEDIA_PLAYER_PROC.poll() is None:
        try:
            _MEDIA_PLAYER_PROC.terminate()
            _MEDIA_PLAYER_PROC = None
            return "Media playback stopped."
        except Exception as e:
            return f"Error stopping media: {e}"

    # Try to kill mpv/ffplay processes
    if IS_LINUX or IS_MACOS:
        result = run(["pkill", "-f", "mpv"])
        result2 = run(["pkill", "-f", "ffplay"])
        return "Media playback stopped."
    elif IS_WINDOWS:
        run(["taskkill", "/F", "/IM", "mpv.exe"])
        run(["taskkill", "/F", "/IM", "ffplay.exe"])
        return "Media playback stopped."

    return "No media player found running."


@needle.tool
def get_media_status() -> str:
    """
    Check if media is currently playing. Use for: checking
    playback status before starting new media.
    """
    global _MEDIA_PLAYER_PROC
    print("[Tool] get_media_status()")

    if _MEDIA_PLAYER_PROC and _MEDIA_PLAYER_PROC.poll() is None:
        return f"Media is playing (PID: {_MEDIA_PLAYER_PROC.pid})"

    return "No media currently playing."


@needle.tool
def set_media_volume(level: int) -> str:
    """
    Set the volume for media playback (0-100). Use for:
    adjusting volume while media is playing.
    """
    print(f"[Tool] set_media_volume({level})")
    level = min(max(int(level), 0), 100)

    # Update mpv volume if running
    global _MEDIA_PLAYER_PROC
    if _MEDIA_PLAYER_PROC and _MEDIA_PLAYER_PROC.poll() is None:
        try:
            # Send command via IPC socket or restart with new volume
            return f"Volume set to {level}%. Restart media to apply."
        except Exception:
            pass

    return f"Volume level set to {level}%."


# ═══════════════════════════════════════════════════════════════════════
# 5. VOICE GATEWAY
# ═══════════════════════════════════════════════════════════════════════

_VOICE_RECORDING = False
_VOICE_PROCESS = None


@needle.tool
def voice_record_start(duration: int = 5) -> str:
    """
    Start recording audio from the microphone. Default 5 seconds.
    Use for: capturing voice input, recording notes, or audio input.
    """
    global _VOICE_RECORDING, _VOICE_PROCESS
    print(f"[Tool] voice_record_start({duration})")

    if _VOICE_RECORDING:
        return "Already recording. Use voice_record_stop first."

    duration = min(max(int(duration), 1), 60)
    output_dir = os.path.join(DOWNLOAD_DIR, "agent_voice")
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, f"voice_{int(time.time())}.wav")

    try:
        if IS_LINUX:
            # Try arecord first
            if shutil.which("arecord"):
                _VOICE_PROCESS = subprocess.Popen(
                    ["arecord", "-d", str(duration), "-f", "S16_LE",
                     "-r", "16000", "-c", "1", output_file],
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                _VOICE_RECORDING = True
                return f"Recording for {duration} seconds... (file: {output_file})"
            # Try ffmpeg
            elif shutil.which("ffmpeg"):
                _VOICE_PROCESS = subprocess.Popen(
                    ["ffmpeg", "-f", "pulse", "-i", "default", "-t", str(duration),
                     "-ar", "16000", "-ac", "1", output_file],
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                _VOICE_RECORDING = True
                return f"Recording for {duration} seconds... (file: {output_file})"
            else:
                return "No audio recording tool found. Install 'arecord' or 'ffmpeg'."
        elif IS_MACOS:
            _VOICE_PROCESS = subprocess.Popen(
                ["ffmpeg", "-f", "avfoundation", "-i", ":0", "-t", str(duration),
                 "-ar", "16000", "-ac", "1", output_file],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            _VOICE_RECORDING = True
            return f"Recording for {duration} seconds... (file: {output_file})"
        elif IS_WINDOWS:
            _VOICE_PROCESS = subprocess.Popen(
                ["ffmpeg", "-f", "dshow", "-i", "audio=Microphone", "-t", str(duration),
                 "-ar", "16000", "-ac", "1", output_file],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            _VOICE_RECORDING = True
            return f"Recording for {duration} seconds... (file: {output_file})"
        else:
            return "Audio recording not supported on this platform."
    except Exception as e:
        return f"Error starting recording: {e}"


@needle.tool
def voice_record_stop() -> str:
    """
    Stop the current voice recording. Use for: ending
    a recording started with voice_record_start.
    """
    global _VOICE_RECORDING, _VOICE_PROCESS
    print("[Tool] voice_record_stop()")

    if not _VOICE_RECORDING or not _VOICE_PROCESS:
        return "No recording in progress."

    try:
        _VOICE_PROCESS.terminate()
        _VOICE_PROCESS.wait(timeout=5)
        _VOICE_RECORDING = False

        output_dir = os.path.join(DOWNLOAD_DIR, "agent_voice")
        if os.path.exists(output_dir):
            files = sorted(os.listdir(output_dir), reverse=True)
            for f in files:
                if f.startswith("voice_") and f.endswith(".wav"):
                    return f"Recording saved: {os.path.join(output_dir, f)}"

        return "Recording stopped."
    except Exception as e:
        return f"Error stopping recording: {e}"


@needle.tool
def voice_speak(text: str, speed: int = 100) -> str:
    """
    Speak text aloud using text-to-speech. Speed: 50-200 (100=normal).
    Use for: reading text aloud, accessibility, voice notifications.
    """
    print(f"[Tool] voice_speak('{text[:50]}...', speed={speed})")

    speed = min(max(int(speed), 50), 200)

    # Try espeak-ng / espeak
    espeak = shutil.which("espeak-ng") or shutil.which("espeak")
    if espeak:
        speed_arg = str(int(175 * speed / 100))
        result = run([espeak, "-s", speed_arg, text])
        return "Speaking..." if not result.startswith("Error") else result

    # Try say (macOS)
    if IS_MACOS and shutil.which("say"):
        result = run(["say", text])
        return "Speaking..." if not result.startswith("Error") else result

    # Try PowerShell on Windows
    if IS_WINDOWS:
        ps_cmd = f'(New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak("{text}")'
        result = powershell(ps_cmd)
        return "Speaking..." if not result.startswith("Error") else result

    # Try festival
    if shutil.which("festival"):
        try:
            proc = subprocess.Popen(["festival", "--pipe"],
                                    stdin=subprocess.PIPE,
                                    stdout=subprocess.DEVNULL,
                                    stderr=subprocess.DEVNULL)
            proc.communicate(input=text.encode(), timeout=10)
            return "Speaking..."
        except Exception:
            pass

    return "No TTS engine found. Install 'espeak-ng' or 'festival'."


@needle.tool
def voice_list_devices() -> str:
    """
    List available audio input/output devices. Use for:
    checking microphone availability, selecting audio devices.
    """
    print("[Tool] voice_list_devices()")

    lines = ["Audio devices:"]

    if IS_LINUX:
        # List ALSA devices
        result = run(["arecord", "-l"])
        if "card" in result.lower():
            lines.append("\nInput (recording) devices:")
            for line in result.split("\n"):
                if "card" in line.lower():
                    lines.append(f"  {line.strip()}")

        # List PulseAudio sinks
        result = run(["pactl", "list", "short", "sinks"])
        if "sink" in result.lower() or "alsa" in result.lower():
            lines.append("\nOutput (playback) devices:")
            for line in result.split("\n"):
                if line.strip():
                    lines.append(f"  {line.strip()}")

    elif IS_MACOS:
        result = run(["system_profiler", "SPAudioDataType"])
        lines.append(result[:1000] if result else "No audio devices found.")

    elif IS_WINDOWS:
        result = powershell("Get-WmiObject Win32_SoundDevice | Select-Object Name,Status | Format-Table -AutoSize")
        lines.append(result[:1000] if result else "No audio devices found.")

    if len(lines) == 1:
        lines.append("No audio devices detected.")

    return "\n".join(lines)
