"""WiFi: _local_ip(), wifi_info(), wifi_scan()."""

import os
import shutil
import socket

from agent.config import IS_WINDOWS, IS_MACOS, IS_LINUX
from agent.runner.common import run, powershell


def _local_ip() -> str:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except OSError:
        return "127.0.0.1"


def wifi_info() -> dict:
    """Return info about the active network connection."""
    if IS_LINUX and shutil.which("nmcli"):
        out = run(["nmcli", "-t", "-f", "active,ssid,signal", "dev", "wifi",
                   "list", "--rescan", "no"], timeout=10)
        for line in out.splitlines():
            p = line.split(":")
            if len(p) >= 3 and p[0] == "yes":
                return {"ssid": p[1], "ip": _local_ip(),
                        "signal": int(p[2]) if p[2].isdigit() else 0,
                        "connected": True}
        # No WiFi link — report ethernet / general connectivity instead
        gen = run(["nmcli", "-t", "-f", "STATE,CONNECTIVITY", "general"],
                  timeout=5)
        devs = run(["nmcli", "-t", "-f", "TYPE,STATE", "device", "status"],
                   timeout=5)
        medium = "wifi"
        for line in devs.splitlines():
            if line.startswith("ethernet:") and "connected" in line:
                medium = "ethernet"
        if "full" in gen.lower() or "limited" in gen.lower() \
                or _local_ip() != "127.0.0.1":
            return {"ssid": None, "ip": _local_ip(), "signal": 0,
                    "connected": True, "medium": medium}
        return {"ssid": None, "ip": _local_ip(), "signal": 0,
                "connected": False}
    if IS_MACOS:
        out = run(["/System/Library/PrivateFrameworks/Apple80211.framework"
                   "/Versions/A/Resources/airport", "-I"], timeout=5)
        ssid = signal = None
        for line in out.splitlines():
            if " SSID:" in line:
                ssid = line.split(":", 1)[1].strip()
            if "agrCtlRSSI:" in line:
                signal = abs(int(line.split(":", 1)[1].strip()))
        return {"ssid": ssid, "ip": _local_ip(),
                "signal": signal or 0, "connected": bool(ssid)}
    if IS_WINDOWS:
        out = powershell('netsh wlan show interfaces | Select-String " SSID|Signal"',
                         timeout=30)
        ssid = signal = None
        for line in out.splitlines():
            if "SSID" in line and "BSSID" not in line and ":" in line:
                ssid = line.split(":", 1)[1].strip()
            if "Signal" in line and ":" in line:
                try:
                    signal = int(line.split(":", 1)[1].strip().rstrip("%"))
                except ValueError:
                    pass
        return {"ssid": ssid or None, "ip": _local_ip(),
                "signal": signal or 0, "connected": bool(ssid)}
    return {"ssid": None, "ip": _local_ip(), "signal": 0, "connected": False}


def wifi_scan() -> list:
    """Scan for nearby WiFi networks."""
    if IS_LINUX and shutil.which("nmcli"):
        out = run(["nmcli", "-t", "-f", "ssid,signal", "dev", "wifi", "list"],
                  timeout=15)
        nets = []
        for line in out.splitlines():
            p = line.split(":")
            if len(p) >= 2 and p[0]:
                nets.append({"ssid": p[0],
                             "signal": int(p[1]) if p[1].isdigit() else 0})
        if nets:
            return nets
        return []
    if IS_MACOS:
        out = run(["/System/Library/PrivateFrameworks/Apple80211.framework"
                   "/Versions/A/Resources/airport", "-s"], timeout=10)
        nets = []
        for line in out.splitlines()[1:]:
            parts = line.split()
            if len(parts) >= 3:
                nets.append({"ssid": parts[0], "signal": abs(int(parts[1]))
                             if parts[1].lstrip("-").isdigit() else 0})
        if nets:
            return nets
        return []
    if IS_WINDOWS:
        out = powershell('netsh wlan show networks mode=bssid | Select-String " SSID|Signal"',
                         timeout=30)
        nets = []
        for line in out.splitlines():
            if "SSID" in line and ":" in line and "BSSID" not in line:
                name = line.split(":", 1)[1].strip()
                if name:
                    nets.append({"ssid": name, "signal": 0})
        if nets:
            return nets
    return []
