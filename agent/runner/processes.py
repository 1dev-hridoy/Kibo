"""Process management: list_processes(), kill_process()."""

import json

from agent.config import IS_WINDOWS, IS_MACOS, IS_LINUX
from agent.runner.common import run, powershell


def list_processes(filter_name: str = "") -> list:
    """List running processes. Optionally filter by name."""
    procs = []
    if IS_LINUX or IS_MACOS:
        out = run(["ps", "aux"], timeout=10)
        if not out.startswith("Error"):
            for line in out.splitlines()[1:]:  # skip header
                parts = line.split(None, 10)
                if len(parts) >= 11:
                    user, pid, cpu, mem = parts[0], parts[1], parts[2], parts[3]
                    cmd = parts[10]
                    if filter_name and filter_name.lower() not in cmd.lower():
                        continue
                    procs.append({"pid": int(pid), "user": user,
                                  "cpu": float(cpu), "mem": float(mem),
                                  "command": cmd[:100]})
    elif IS_WINDOWS:
        script = 'Get-Process | Select-Object Id, ProcessName, CPU, WorkingSet64 | ConvertTo-Json'
        out = powershell(script, timeout=30)
        if not out.startswith("Error"):
            try:
                data = json.loads(out)
                if isinstance(data, dict):
                    data = [data]
                for p in (data or []):
                    name = p.get("ProcessName", "")
                    if filter_name and filter_name.lower() not in name.lower():
                        continue
                    procs.append({"pid": p.get("Id", 0), "user": "",
                                  "cpu": round(p.get("CPU", 0) or 0, 1),
                                  "mem": round((p.get("WorkingSet64", 0) or 0) / 1048576, 1),
                                  "command": name})
            except (json.JSONDecodeError, TypeError):
                pass
    return sorted(procs, key=lambda x: x.get("cpu", 0), reverse=True)[:50]


def kill_process(pid: int) -> str:
    """Kill a process by PID."""
    try:
        pid = int(pid)
    except (TypeError, ValueError):
        return f"Error: invalid PID '{pid}'"
    if IS_LINUX or IS_MACOS:
        res = run(["kill", "-9", str(pid)], timeout=5)
        return f"Process {pid} killed." if not res.startswith("Error") else res
    elif IS_WINDOWS:
        res = powershell(f"Stop-Process -Id {pid} -Force", timeout=10)
        return f"Process {pid} killed." if not res.startswith("Error") else res
    return "Error: cannot kill process on this system."
