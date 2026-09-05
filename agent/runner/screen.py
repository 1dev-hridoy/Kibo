"""Screen: take_screenshot(), lock_screen(), _lock_windows()."""

import os
import shutil

from agent.config import IS_WINDOWS, IS_MACOS, IS_LINUX
from agent.runner.common import run, powershell


def take_screenshot() -> str:
    """Capture the full screen and save it as a PNG in ~/Downloads."""
    from agent.config import SCREENSHOT_PATHS
    dest = SCREENSHOT_PATHS[0]
    os.makedirs(os.path.dirname(dest), exist_ok=True)

    if IS_LINUX:
        # Wayland compositors first, then X11 tools, then desktop portals
        if shutil.which("grim") and os.environ.get("WAYLAND_DISPLAY"):
            res = run(["grim", dest])
            if not res.startswith("Error"):
                return f"Screenshot saved to {dest}"
        if shutil.which("gnome-screenshot"):
            res = run(["gnome-screenshot", "-f", dest])
            if not res.startswith("Error"):
                return f"Screenshot saved to {dest}"
        if shutil.which("scrot"):
            res = run(["scrot", dest])
            if not res.startswith("Error"):
                return f"Screenshot saved to {dest}"
        import shutil as _sh
        portal = _sh.which("grim")
        if portal:
            res = run(["grim", dest])
            if not res.startswith("Error"):
                return f"Screenshot saved to {dest}"
        return ("Screenshot failed — install a capture tool "
                "(gnome-screenshot, scrot, or grim for Wayland)")
    if IS_MACOS:
        res = run(["screencapture", "-x", dest])
        return f"Screenshot saved to {dest}" if res == "Success" else res
    if IS_WINDOWS:
        script = '''Add-Type -AssemblyName System.Windows.Forms,System.Drawing
$b = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds
$bmp = New-Object System.Drawing.Bitmap $b.Width, $b.Height
$g = [System.Drawing.Graphics]::FromImage($bmp)
$g.CopyFromScreen($b.Location, [System.Drawing.Point]::Empty, $b.Size)
$bmp.Save(\"''' + dest.replace("\\", "/") + '''\")
$g.Dispose(); $bmp.Dispose()
Write-Output 'Success'
'''
        res = powershell(script, timeout=60)
        return f"Screenshot saved to {dest}" if res == "Success" else res
    return "Screenshot is not supported on this system."


def lock_screen() -> str:
    """Lock the workstation / screen."""
    if IS_LINUX:
        for cmd in (["loginctl", "lock-session"],
                    ["gnome-screensaver-command", "-l"],
                    ["xscreensaver-command", "-lock"]):
            if shutil.which(cmd[0]):
                res = run(cmd)
                if not res.startswith("Error"):
                    return "Screen locked"
        return "Screen lock failed — no supported lock command found."
    if IS_MACOS:
        return run(["pmset", "displaysleepnow"]) or "Screen locked"
    if IS_WINDOWS:
        return _lock_windows()
    return "Screen lock is not supported on this system."


def _lock_windows() -> str:
    import ctypes
    ctypes.windll.user32.LockWorkStation()
    return "Screen locked"
