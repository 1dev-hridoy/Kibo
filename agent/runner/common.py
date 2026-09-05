"""Shared helpers: run(), run_cmd(), run_cmd_json(), powershell(), _find(), _pkg_hint(), CREATE_NO_WINDOW."""

import base64
import json
import os
import shutil
import subprocess

from agent.config import (
    CMD_TIMEOUT, IS_WINDOWS, IS_MACOS, IS_LINUX, LINUX_DISTRO,
)

CREATE_NO_WINDOW = 0x08000000 if IS_WINDOWS else 0


def _find(*names):
    """Return the first existing binary among names, else None."""
    for n in names:
        path = shutil.which(n)
        if path:
            return path
    return None


def _pkg_hint(apt, dnf, pacman, zypper, apk):
    """Return the distro-appropriate install command for a package."""
    if IS_LINUX:
        hint = {"apt": apt, "dnf": dnf, "pacman": pacman,
                "zypper": zypper, "apk": apk}
        mgr = {"ubuntu": "apt", "debian": "apt", "linuxmint": "apt",
               "fedora": "dnf", "rhel": "dnf", "centos": "dnf",
               "arch": "pacman", "manjaro": "pacman", "endeavouros": "pacman",
               "cachyos": "pacman", "opensuse": "zypper",
               "alpine": "apk"}.get(LINUX_DISTRO)
        if mgr:
            return hint.get(mgr, "")
    return ""


def run(argv, timeout: int = CMD_TIMEOUT) -> str:
    """Execute a native command and return its output (generic helper)."""
    try:
        kwargs = {}
        if IS_WINDOWS:
            kwargs["creationflags"] = CREATE_NO_WINDOW
        res = subprocess.run(argv, capture_output=True, text=True,
                             errors="replace", timeout=timeout, **kwargs)
        if res.returncode == 0:
            return res.stdout.strip() if res.stdout.strip() else "Success"
        err = res.stderr.strip() or res.stdout.strip() or f"Exit code {res.returncode}"
        return f"Error ({argv[0]}): {err}"
    except subprocess.TimeoutExpired:
        return f"Error ({argv[0]}): Timed out after {timeout}s."
    except (FileNotFoundError, PermissionError, OSError) as e:
        return f"Error ({argv[0]}): {e}"


# Convenience aliases for user-defined custom tools
run_cmd = run


def run_cmd_json(argv, timeout: int = CMD_TIMEOUT):
    """Execute a command and parse its JSON output."""
    res = run(argv, timeout)
    try:
        return json.loads(res)
    except (json.JSONDecodeError, TypeError):
        return res


if IS_WINDOWS:
    def powershell(script: str, timeout: int = 60) -> str:
        """Run a PowerShell script (base64-encoded, windowless). Returns stdout."""
        encoded = base64.b64encode(script.encode("utf-16-le")).decode("ascii")
        try:
            res = subprocess.run(
                ["powershell", "-NoProfile", "-NonInteractive",
                 "-ExecutionPolicy", "Bypass", "-EncodedCommand", encoded],
                capture_output=True, text=True, errors="replace",
                timeout=timeout, creationflags=CREATE_NO_WINDOW)
            if res.returncode == 0:
                return res.stdout.strip()
            err = res.stderr.strip() or f"Exit code {res.returncode}"
            return f"Error: {err}"
        except subprocess.TimeoutExpired:
            return f"Error: PowerShell timed out after {timeout}s."
        except (FileNotFoundError, OSError) as e:
            return f"Error: PowerShell unavailable ({e})."
else:
    def powershell(script: str, timeout: int = 60) -> str:
        return "Error: PowerShell is only available on Windows."
