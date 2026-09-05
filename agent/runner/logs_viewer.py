"""Log viewing: view_logs()."""

import os

from agent.config import IS_WINDOWS, IS_MACOS, IS_LINUX
from agent.runner.common import run, powershell
from agent.runner.files import file_read


def view_logs(log_type: str = "system", lines: int = 30, grep: str = "") -> str:
    """View system or application logs.
    log_type: 'system', 'auth', 'kernel', 'journal', or a file path.
    """
    result = ""
    if IS_LINUX:
        if log_type == "system":
            out = run(["journalctl", "-n", str(lines), "--no-pager"], timeout=10)
            result = out
        elif log_type == "auth":
            out = run(["journalctl", "-n", str(lines), "-u", "sshd", "--no-pager"], timeout=10)
            result = out
        elif log_type == "kernel":
            out = run(["journalctl", "-n", str(lines), "-k", "--no-pager"], timeout=10)
            result = out
        elif log_type == "journal":
            out = run(["journalctl", "-n", str(lines), "--no-pager", "-o", "short-iso"], timeout=10)
            result = out
        elif os.path.exists(log_type):
            result = file_read(log_type, lines)
        else:
            # Try as a systemd unit
            out = run(["journalctl", "-n", str(lines), "-u", log_type, "--no-pager"], timeout=10)
            result = out
    elif IS_MACOS:
        if log_type == "system":
            out = run(["log", "show", "--last", "1h", "--style", "compact"], timeout=15)
            result = out
        elif os.path.exists(log_type):
            result = file_read(log_type, lines)
        else:
            result = f"Log type '{log_type}' not supported on macOS."
    elif IS_WINDOWS:
        if log_type == "system":
            script = f'Get-EventLog -LogName System -Newest {lines} | Format-Table TimeGenerated, Source, Message -AutoSize'
            result = powershell(script, timeout=30)
        elif log_type == "application":
            script = f'Get-EventLog -LogName Application -Newest {lines} | Format-Table TimeGenerated, Source, Message -AutoSize'
            result = powershell(script, timeout=30)
        elif os.path.exists(log_type):
            result = file_read(log_type, lines)
        else:
            result = f"Log type '{log_type}' not supported. Try 'system' or 'application'."
    else:
        result = "Log viewing not supported on this system."

    if grep and not result.startswith("Error"):
        filtered = [l for l in result.splitlines() if grep.lower() in l.lower()]
        result = "\n".join(filtered[:lines]) if filtered else f"No matches for '{grep}'"
    return result
