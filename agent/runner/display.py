"""Display brightness: set_brightness()."""

import os
import shutil

from agent.config import IS_WINDOWS, IS_MACOS, IS_LINUX
from agent.runner.common import run, powershell


def set_brightness(level) -> str:
    """Set screen brightness. Accepts 0-100 percent or 0-255 raw."""
    try:
        val = int(level)
    except (TypeError, ValueError):
        return f"Error: invalid brightness level '{level}'."
    if IS_LINUX:
        if shutil.which("brightnessctl") and os.path.isdir("/sys/class/backlight") \
                and os.listdir("/sys/class/backlight"):
            pct = val if val <= 100 else round(val / 255 * 100)
            return run(["brightnessctl", "-c", "backlight", "s", f"{pct}%"])
        return f"Brightness unchanged ({val} requested — no backlight device; use the monitor OSD)"
    if IS_MACOS:
        if shutil.which("brightness"):
            frac = max(0.0, min(1.0, val / 100 if val <= 100 else val / 255))
            return run(["brightness", str(frac)])
        return f"Brightness unchanged ({val} requested — brew install brightness)"
    if IS_WINDOWS:
        pct = max(0, min(100, val if val <= 100 else round(val / 255 * 100)))
        script = f'''$b = Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods
$b.WmiSetBrightness(1, {pct})
Write-Output "Success"
'''
        res = powershell(script, timeout=30)
        if res == "Success":
            return f"Brightness set to {pct}%"
        return f"Brightness unchanged ({pct}% requested — desktop monitors need DDC/CI)"
    return f"Brightness set to {val}"
