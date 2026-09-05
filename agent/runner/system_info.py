"""System information: system_info(), device_info(), has_internet(), system_stats()."""

import json
import os
import platform as _pyplatform
import re
import socket

from agent.config import (
    IS_WINDOWS, IS_MACOS, IS_LINUX, LINUX_DISTRO, PLATFORM_NAME,
)
from agent.runner.common import run, powershell
from agent.runner.wifi import _local_ip


def system_info() -> dict:
    """Return host system information."""
    return {
        "platform": PLATFORM_NAME,
        "distro": LINUX_DISTRO if IS_LINUX else None,
        "hostname": _pyplatform.node(),
        "python": _pyplatform.python_version(),
        "machine": _pyplatform.machine(),
        "ip": _local_ip(),
    }


def device_info() -> dict:
    """Device/host identity: model, OS, hostname-style identifier."""
    if IS_LINUX:
        model = ""
        try:
            with open("/sys/devices/virtual/dmi/id/product_name") as f:
                model = f.read().strip()
        except OSError:
            pass
        return {"model": model or "Unknown Linux PC",
                "os": f"Linux {LINUX_DISTRO.title()}" if LINUX_DISTRO else "Linux",
                "serial": _pyplatform.node(),
                "type": "desktop"}
    if IS_MACOS:
        out = run(["sysctl", "-n", "hw.model"])
        ok = out and not out.startswith("Error")
        return {"model": out if ok else "Mac",
                "os": f"macOS {_pyplatform.mac_ver()[0]}",
                "serial": _pyplatform.node(),
                "type": "desktop"}
    if IS_WINDOWS:
        out = powershell("(Get-CimInstance Win32_ComputerSystem).Model", timeout=30)
        ok = out and not out.startswith("Error")
        return {"model": out if ok else "Windows PC",
                "os": f"Windows {_pyplatform.release()}",
                "serial": _pyplatform.node(),
                "type": "desktop"}
    return {"model": "Unknown", "os": PLATFORM_NAME, "serial": "?",
            "type": "desktop"}


def has_internet() -> bool:
    """Quick connectivity probe via DNS resolution."""
    try:
        socket.gethostbyname("cloudflare.com")
        return True
    except OSError:
        return False


def system_stats() -> dict:
    """CPU load and RAM usage snapshot (no third-party deps)."""
    stats = {}
    if IS_LINUX:
        try:
            with open("/proc/loadavg") as f:
                parts = f.read().split()
            stats["load1"] = float(parts[0])
            stats["load5"] = float(parts[1])
            ncpu = os.cpu_count() or 1
            stats["cpu_percent"] = round(float(parts[0]) / ncpu * 100, 1)
        except (OSError, ValueError, IndexError):
            pass
        try:
            mem = {}
            with open("/proc/meminfo") as f:
                for line in f:
                    k, _, v = line.partition(":")
                    mem[k.strip()] = int(v.strip().split()[0])  # kB
            total = mem.get("MemTotal", 0)
            avail = mem.get("MemAvailable", 0)
            if total:
                used = total - avail
                stats["mem_total_gb"] = round(total / 1048576, 1)
                stats["mem_used_gb"] = round(used / 1048576, 1)
                stats["mem_percent"] = round(used / total * 100, 1)
        except (OSError, ValueError):
            pass
    elif IS_MACOS:
        out = run(["top", "-l", "1", "-n", "0"], timeout=15)
        m = re.search(r"CPU usage:.*?([\d.]+)% idle", out)
        if m:
            stats["cpu_percent"] = round(100 - float(m.group(1)), 1)
        m = re.search(r"PhysMem:\s*(\d+)([GM]) used", out)
        if m:
            used_g = float(m.group(1)) if m.group(2) == "G" \
                else float(m.group(1)) / 1024
            stats["mem_used_gb"] = round(used_g, 1)
        out = run(["sysctl", "-n", "hw.memsize"], timeout=5)
        try:
            stats["mem_total_gb"] = round(int(out) / 1073741824, 1)
        except ValueError:
            pass
        if "mem_total_gb" in stats and "mem_used_gb" in stats:
            stats["mem_percent"] = round(
                stats["mem_used_gb"] / stats["mem_total_gb"] * 100, 1)
    else:  # Windows
        script = ('$cpu = (Get-CimInstance Win32_Processor | '
                  'Measure-Object -Property LoadPercentage -Average).Average\n'
                  '$os = Get-CimInstance Win32_OperatingSystem\n'
                  'Write-Output "$cpu,$($os.TotalVisibleMemorySize),'
                  '$($os.FreePhysicalMemory)"')
        out = powershell(script, timeout=30)
        try:
            cpu_s, tot_s, free_s = out.split(",")
            stats["cpu_percent"] = round(float(cpu_s), 1)
            tot_kb = int(tot_s)
            free_kb = int(free_s)
            used_kb = tot_kb - free_kb
            stats["mem_total_gb"] = round(tot_kb / 1048576, 1)
            stats["mem_used_gb"] = round(used_kb / 1048576, 1)
            stats["mem_percent"] = round(used_kb / tot_kb * 100, 1)
        except (ValueError, IndexError):
            pass
    return stats
