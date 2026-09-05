"""
Centralized configuration for the Agent — cross-platform PC edition.
Detects the operating system at runtime and provides OS-appropriate
paths, app launchers and native binary probes for Linux, Windows and macOS.
"""

import os
import shutil
import sys
import platform as _pyplatform

# ── Load .env file if present ──────────────────────────────────────────
try:
    from dotenv import load_dotenv
    _env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
    if os.path.exists(_env_path):
        load_dotenv(_env_path)
except ImportError:
    pass

# ── Platform identity ─────────────────────────────────────────────────
if os.name == "nt":
    PLATFORM = "windows"
elif sys.platform == "darwin":
    PLATFORM = "macos"
else:
    PLATFORM = "linux"

IS_WINDOWS = PLATFORM == "windows"
IS_MACOS = PLATFORM == "macos"
IS_LINUX = PLATFORM == "linux"

PLATFORM_NAME = {"windows": "Windows", "macos": "macOS"}.get(
    PLATFORM, "Linux")

# Linux distribution (for package-manager hints)
LINUX_DISTRO = ""
if IS_LINUX:
    try:
        with open("/etc/os-release") as _f:
            for _line in _f:
                if _line.startswith("ID="):
                    LINUX_DISTRO = _line.split("=", 1)[1].strip().strip('"').lower()
                    break
    except OSError:
        pass

# ── Paths ──────────────────────────────────────────────────────────────
HOME = os.path.expanduser("~")
DOWNLOAD_DIR = os.path.join(HOME, "Downloads")
if not os.path.isdir(DOWNLOAD_DIR):
    DOWNLOAD_DIR = HOME
PHOTO_SAVE_DIR = os.path.join(DOWNLOAD_DIR, "agent_photos")
AUDIO_SAVE_DIR = os.path.join(DOWNLOAD_DIR, "agent_recordings")
SCREENSHOT_DIR = os.path.join(DOWNLOAD_DIR, "agent_screenshots")

PHOTO_PATHS = [
    os.path.join(PHOTO_SAVE_DIR, "agent_photo.jpg"),
    os.path.join(DOWNLOAD_DIR, "agent_photo.jpg"),
    os.path.join(HOME, "agent_photo.jpg"),
]

SCREENSHOT_PATHS = [
    os.path.join(SCREENSHOT_DIR, "agent_screenshot.png"),
    os.path.join(DOWNLOAD_DIR, "agent_screenshot.png"),
    os.path.join(HOME, "agent_screenshot.png"),
]

# ── Command execution ──────────────────────────────────────────────────
CMD_TIMEOUT = 15  # seconds

# ── Web server ─────────────────────────────────────────────────────────
WEB_HOST = os.environ.get("AGENT_HOST",
                          os.environ.get("HARNESS_HOST", "127.0.0.1"))
WEB_PORT = int(os.environ.get("AGENT_PORT",
                              os.environ.get("HARNESS_PORT", 5000)))

# ── Telegram (set via env or CLI flag) ─────────────────────────────────
TELEGRAM_TOKEN = os.environ.get(
    "AGENT_TELEGRAM_TOKEN", os.environ.get("HARNESS_TELEGRAM_TOKEN", ""))

# ── Native helper binaries (probed once at import) ─────────────────────
def _which(name):
    return shutil.which(name)

if IS_LINUX:
    HAS_NOTIFY_SEND = bool(_which("notify-send"))
    HAS_PACTL = bool(_which("pactl"))
    HAS_NMCLI = bool(_which("nmcli"))
    HAS_ESPEAK = bool(_which("espeak-ng") or _which("espeak"))
    HAS_UPOWER = bool(_which("upower"))
    HAS_BRIGHTNESSCTL = bool(_which("brightnessctl"))
    HAS_FFMPEG = bool(_which("ffmpeg"))
    HAS_WL_COPY = bool(_which("wl-copy"))
    HAS_XCLIP = bool(_which("xclip"))
    HAS_GNOME_SCREENSHOT = bool(_which("gnome-screenshot"))
    HAS_SCROT = bool(_which("scrot"))
    HAS_GRIM = bool(_which("grim"))
elif IS_MACOS:
    HAS_NOTIFY_SEND = False
    HAS_PACTL = False
    HAS_NMCLI = False
    HAS_ESPEAK = False
    HAS_UPOWER = False
    HAS_BRIGHTNESSCTL = bool(_which("brightness"))
    HAS_FFMPEG = bool(_which("ffmpeg"))
    HAS_WL_COPY = False
    HAS_XCLIP = False
    HAS_GNOME_SCREENSHOT = False
    HAS_SCROT = False
    HAS_GRIM = False
else:  # windows
    HAS_NOTIFY_SEND = True   # via PowerShell toast
    HAS_PACTL = False
    HAS_NMCLI = False        # via netsh
    HAS_ESPEAK = True        # via SAPI (System.Speech)
    HAS_UPOWER = False
    HAS_BRIGHTNESSCTL = True # via WMI (laptops)
    HAS_FFMPEG = bool(_which("ffmpeg"))
    HAS_WL_COPY = False
    HAS_XCLIP = False
    HAS_GNOME_SCREENSHOT = False
    HAS_SCROT = False
    HAS_GRIM = False

# ── Host info (shown in the web UI / logs) ─────────────────────────────
HOSTNAME = _pyplatform.node() or "localhost"
