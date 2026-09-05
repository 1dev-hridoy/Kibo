"""Clipboard: clipboard_set(), clipboard_get()."""

import os
import shutil
import subprocess

from agent.config import CMD_TIMEOUT, IS_WINDOWS, IS_MACOS, IS_LINUX
from agent.runner.common import run, powershell


def clipboard_set(text: str) -> str:
    """Copy text to the system clipboard."""
    if IS_LINUX:
        if os.environ.get("WAYLAND_DISPLAY") and shutil.which("wl-copy"):
            try:
                subprocess.Popen(["wl-copy", text], stdout=subprocess.DEVNULL,
                                 stderr=subprocess.DEVNULL, start_new_session=True)
                return "Success"
            except OSError:
                pass
        if shutil.which("xclip"):
            try:
                res = subprocess.run(["xclip", "-selection", "clipboard"],
                                     input=text, capture_output=True, text=True,
                                     timeout=CMD_TIMEOUT)
                return "Success" if res.returncode == 0 else f"Error: {res.stderr.strip()}"
            except (OSError, subprocess.SubprocessError) as e:
                return f"Error: {e}"
        return "Clipboard not set (install wl-clipboard or xclip)"
    if IS_MACOS:
        try:
            res = subprocess.run(["pbcopy"], input=text, capture_output=True,
                                 text=True, timeout=CMD_TIMEOUT)
            return "Success" if res.returncode == 0 else f"Error: {res.stderr.strip()}"
        except (OSError, subprocess.SubprocessError) as e:
            return f"Error: {e}"
    if IS_WINDOWS:
        res = powershell(f"Set-Clipboard -Value '{text}'", timeout=30)
        return "Success" if res == "Success" else res
    return "Clipboard not set (no clipboard tool available)"


def clipboard_get() -> str:
    """Read text from the system clipboard."""
    if IS_LINUX:
        if os.environ.get("WAYLAND_DISPLAY") and shutil.which("wl-paste"):
            out = run(["wl-paste"], timeout=5)
            return out if out != "Success" else ""
        if shutil.which("xclip"):
            return run(["xclip", "-selection", "clipboard", "-o"], timeout=5)
        return "Clipboard is empty (install wl-clipboard or xclip)"
    if IS_MACOS:
        return run(["pbpaste"], timeout=5)
    if IS_WINDOWS:
        return powershell("Get-Clipboard", timeout=30)
    return "Clipboard is unavailable on this system."
