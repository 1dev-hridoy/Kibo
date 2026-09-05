"""Disk and temperature: disk_usage(), system_temperature()."""

import json
import os

from agent.config import IS_WINDOWS, IS_MACOS, IS_LINUX
from agent.runner.common import run, powershell


def disk_usage() -> list:
    """Return disk usage for all mounted partitions."""
    disks = []
    if IS_LINUX or IS_MACOS:
        out = run(["df", "-h", "--output=source,size,used,avail,pcent,target"], timeout=10)
        if out.startswith("Error"):
            out = run(["df", "-h"], timeout=10)
        for line in out.splitlines()[1:]:
            parts = line.split()
            if len(parts) >= 6 and parts[0].startswith("/"):
                disks.append({"device": parts[0], "total": parts[1],
                              "used": parts[2], "available": parts[3],
                              "percent": parts[4], "mount": parts[5]})
    elif IS_WINDOWS:
        script = '''Get-CimInstance Win32_LogicalDisk | Where-Object {$_.DriveType -eq 3} |
            Select-Object DeviceID, @{N="SizeGB";E={[math]::Round($_.Size/1GB,1)}},
            @{N="FreeGB";E={[math]::Round($_.FreeSpace/1GB,1)}} | ConvertTo-Json'''
        out = powershell(script, timeout=30)
        if not out.startswith("Error"):
            try:
                data = json.loads(out)
                if isinstance(data, dict):
                    data = [data]
                for d in (data or []):
                    total = d.get("SizeGB", 0)
                    free = d.get("FreeGB", 0)
                    used = round(total - free, 1)
                    pct = round(used / total * 100, 1) if total else 0
                    disks.append({"device": d.get("DeviceID", ""),
                                  "total": f"{total}GB", "used": f"{used}GB",
                                  "available": f"{free}GB",
                                  "percent": f"{pct}%", "mount": d.get("DeviceID", "")})
            except (json.JSONDecodeError, TypeError):
                pass
    return disks


def system_temperature() -> dict:
    """Read system temperature sensors if available."""
    temps = {}
    if IS_LINUX:
        # Try thermal zones
        thermal = "/sys/class/thermal"
        if os.path.isdir(thermal):
            for entry in os.listdir(thermal):
                if entry.startswith("thermal_zone"):
                    try:
                        with open(os.path.join(thermal, entry, "type")) as f:
                            name = f.read().strip()
                        with open(os.path.join(thermal, entry, "temp")) as f:
                            temp = int(f.read().strip()) / 1000
                        temps[name] = round(temp, 1)
                    except (OSError, ValueError):
                        pass
        # Try hwmon
        hwmon = "/sys/class/hwmon"
        if os.path.isdir(hwmon):
            for device in os.listdir(hwmon):
                device_path = os.path.join(hwmon, device)
                try:
                    with open(os.path.join(device_path, "name")) as f:
                        name = f.read().strip()
                except OSError:
                    name = device
                for entry in os.listdir(device_path):
                    if entry.startswith("temp") and entry.endswith("_input"):
                        try:
                            with open(os.path.join(device_path, entry)) as f:
                                temp = int(f.read().strip()) / 1000
                            if 0 < temp < 200:
                                temps[f"{name}_{entry}"] = round(temp, 1)
                        except (OSError, ValueError):
                            pass
    elif IS_MACOS:
        out = run(["osx-cpu-temp"], timeout=5)
        if not out.startswith("Error") and "C" in out:
            temps["CPU"] = out.strip()
    return temps
