"""
Multi-PC support — register and switch between multiple computers.
"""

import os
import json
import time
import subprocess

PCS_FILE = os.path.expanduser("~/.kibo_pcs.json")
_active_pc = "local"


def _load_pcs():
    """Load PC list from disk."""
    if os.path.exists(PCS_FILE):
        with open(PCS_FILE) as f:
            return json.load(f)
    return {}


def _save_pcs(pcs):
    """Save PC list to disk."""
    with open(PCS_FILE, "w") as f:
        json.dump(pcs, f, indent=2)


def register_pc(name, host, port=5000, username="", key_path=""):
    """Register a remote PC.
    
    Args:
        name: Friendly name for the PC
        host: IP address or hostname
        port: Web API port (default 5000)
        username: SSH username (for remote execution)
        key_path: Path to SSH key (for remote execution)
    """
    pcs = _load_pcs()
    pcs[name] = {
        "host": host,
        "port": port,
        "username": username,
        "key_path": key_path,
        "registered": time.time(),
        "last_seen": None,
    }
    _save_pcs(pcs)
    return f"Registered PC: {name} ({host}:{port})"


def unregister_pc(name):
    """Remove a registered PC."""
    pcs = _load_pcs()
    if name in pcs:
        del pcs[name]
        _save_pcs(pcs)
        return f"Unregistered PC: {name}"
    return f"PC not found: {name}"


def list_pcs():
    """List all registered PCs."""
    pcs = _load_pcs()
    if not pcs:
        return "No PCs registered (only local)"

    result = "Registered PCs:\n"
    for name, info in pcs.items():
        status = "LOCAL" if name == "local" else "REMOTE"
        result += f"  - {name} ({info['host']}:{info['port']}) [{status}]\n"
    return result


def switch_pc(name):
    """Switch to a different PC."""
    global _active_pc
    pcs = _load_pcs()
    if name == "local":
        _active_pc = "local"
        return "Switched to local PC"
    if name in pcs:
        _active_pc = name
        return f"Switched to: {name} ({pcs[name]['host']}:{pcs[name]['port']})"
    return f"PC not found: {name}"


def get_active_pc():
    """Get the currently active PC."""
    if _active_pc == "local":
        return {"name": "local", "host": "127.0.0.1", "port": 5000, "local": True}
    pcs = _load_pcs()
    if _active_pc in pcs:
        info = pcs[_active_pc].copy()
        info["name"] = _active_pc
        info["local"] = False
        return info
    return {"name": "local", "host": "127.0.0.1", "port": 5000, "local": True}


def _ssh_cmd(host, username, key_path, command):
    """Execute a command on a remote PC via SSH."""
    ssh_args = ["ssh", "-o", "ConnectTimeout=5"]
    if key_path:
        ssh_args.extend(["-i", key_path])
    if username:
        ssh_args.append(f"{username}@{host}")
    else:
        ssh_args.append(host)
    ssh_args.append(command)

    try:
        result = subprocess.run(
            ssh_args, capture_output=True, text=True, timeout=30
        )
        return result.stdout.strip(), result.returncode
    except subprocess.TimeoutExpired:
        return "SSH connection timed out", 1
    except Exception as e:
        return f"SSH error: {e}", 1


def execute_on_pc(pc_name, command):
    """Execute a command on a specific PC."""
    if pc_name == "local":
        try:
            result = subprocess.run(
                command, shell=True, capture_output=True, text=True, timeout=30
            )
            return result.stdout.strip()
        except Exception as e:
            return f"Error: {e}"

    pcs = _load_pcs()
    if pc_name not in pcs:
        return f"PC not found: {pc_name}"

    info = pcs[pc_name]
    output, code = _ssh_cmd(
        info["host"], info.get("username", ""),
        info.get("key_path", ""), command
    )
    return output


def ping_pc(pc_name):
    """Check if a PC is reachable."""
    pcs = _load_pcs()
    if pc_name == "local":
        return "Local PC is always reachable"

    if pc_name not in pcs:
        return f"PC not found: {pc_name}"

    info = pcs[pc_name]
    try:
        result = subprocess.run(
            ["ping", "-c", "1", "-W", "2", info["host"]],
            capture_output=True, timeout=5
        )
        if result.returncode == 0:
            return f"{pc_name} is online ({info['host']})"
        return f"{pc_name} is offline"
    except Exception:
        return f"Could not ping {pc_name}"
