"""Battery: has_battery(), battery_status(), _linux_battery()."""

import os
import re
import shutil

from agent.config import IS_WINDOWS, IS_MACOS, IS_LINUX
from agent.runner.common import run, powershell


def has_battery() -> bool:
    """True when the machine has a real battery (laptop / UPS)."""
    if IS_LINUX:
        base = "/sys/class/power_supply"
        if os.path.isdir(base):
            for entry in os.listdir(base):
                if entry.upper().startswith(("BAT", "CMB")):
                    return True
        return False
    if IS_MACOS:
        return "Battery" in run(["pmset", "-g", "batt"], timeout=5)
    # Windows: no Win32_Battery instance on desktops
    out = powershell("(Get-CimInstance Win32_Battery) -ne $null", timeout=30)
    return out.strip().lower() == "true"


def battery_status() -> dict | None:
    """Return battery info, or None when the machine has no battery."""
    if not has_battery():
        return None
    if IS_LINUX:
        return _linux_battery()
    if IS_MACOS:
        out = run(["pmset", "-g", "batt"])
        try:
            pct = int(out.split("%")[0].split()[-1])
            charging = "AC Power" in out or "charging" in out
            return {"percent": pct, "status": "CHARGING" if charging else "DISCHARGING",
                    "plugged": charging, "temperature": None}
        except (ValueError, IndexError):
            return None
    # Windows
    out = powershell('''$b = Get-CimInstance Win32_Battery
if ($b) { Write-Output "$($b.EstimatedChargeRemaining),$($b.BatteryStatus)" }
''', timeout=30)
    try:
        pct_s, st_s = out.split(",")
        pct = int(float(pct_s))
        st = int(st_s.strip())
        # BatteryStatus: 1=discharging, 2=on AC
        return {"percent": pct,
                "status": "CHARGING" if st == 2 else "DISCHARGING",
                "plugged": st == 2, "temperature": None}
    except (ValueError, IndexError):
        return None


def _linux_battery():
    base = "/sys/class/power_supply"
    bat = None
    if os.path.isdir(base):
        for name in ("BAT0", "BAT1", "BATT"):
            if os.path.isdir(os.path.join(base, name)):
                bat = os.path.join(base, name)
                break
        if bat is None:
            for entry in os.listdir(base):
                if entry.upper().startswith("BAT"):
                    bat = os.path.join(base, entry)
                    break
    if bat:
        def _rd(p):
            try:
                with open(p) as f:
                    return f.read().strip()
            except OSError:
                return ""
        pct = _rd(os.path.join(bat, "capacity"))
        status = _rd(os.path.join(bat, "status")) or "Unknown"
        if pct:
            temp = None
            t = _rd(os.path.join(bat, "temp"))
            if t:
                try:
                    temp = float(t) / 10.0
                except ValueError:
                    pass
            return {"percent": int(pct),
                    "status": status.upper(),
                    "plugged": "harg" in status or "Full" in status,
                    "temperature": temp}
    if shutil.which("upower"):
        out = run(["upower", "--dump"], timeout=5)
        m = re.search(r"percentage:\s*([\d.]+)%", out)
        s = re.search(r"state:\s*(\S+)", out)
        if m:
            st = s.group(1) if s else "unknown"
            pct = int(float(m.group(1)))
            # Desktops expose a dummy 0%/unknown entry — reject it.
            if pct > 0 or st.lower() in ("charging", "discharging",
                                         "fully-charged"):
                return {"percent": pct, "status": st.upper(),
                        "plugged": "charg" in st.lower(),
                        "temperature": None}
    return None
