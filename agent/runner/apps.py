"""App/URL launching and downloads: _startfile(), launch(), open_url(), open_path(), copy_to_clipboard(), download_file()."""

import os
import re
import shutil
import subprocess

from agent.config import (
    IS_WINDOWS, IS_MACOS, IS_LINUX, DOWNLOAD_DIR,
)
from agent.runner.common import run, powershell
from agent.runner.clipboard import clipboard_set


def _startfile(target: str) -> str:
    """Open a file/URL with the OS default handler (Windows)."""
    try:
        os.startfile(target)  # noqa: attribute exists on Windows
        return "Success"
    except OSError as e:
        return f"Error: {e}"


def launch(app_name: str) -> str:
    """Open a named app or website via the default browser / native launcher."""
    from agent.config_apps import APP_URLS, LINUX_APPS, WINDOWS_APPS, MACOS_APPS

    key = app_name.strip().lower()
    if key in APP_URLS:
        return open_url(APP_URLS[key])

    if IS_LINUX:
        cmd = LINUX_APPS.get(key)
        if cmd:
            if shutil.which(cmd[0]):
                return run(cmd)
            return f"'{app_name}' isn't installed (no {cmd[0]} on PATH)"
    elif IS_MACOS:
        cmd = MACOS_APPS.get(key)
        if cmd:
            return run(["open", "-a"] + cmd)
    elif IS_WINDOWS:
        cmd = WINDOWS_APPS.get(key)
        if cmd:
            if cmd[0].endswith(":"):  # URI scheme e.g. ms-settings:, camera:
                return _startfile(cmd[0])
            return _startfile(cmd[0])

    # Last resort: try the name as a URL
    if "." in key and " " not in key:
        return open_url(f"https://{key}")

    return f"Couldn't find an app or website called '{app_name}'."


def open_url(url: str) -> str:
    """Open a URL in the default browser."""
    if IS_LINUX and shutil.which("xdg-open"):
        try:
            subprocess.Popen(["xdg-open", url], stdout=subprocess.DEVNULL,
                             stderr=subprocess.DEVNULL, start_new_session=True)
            return "Success"
        except OSError as e:
            return f"Error: {e}"
    if IS_MACOS:
        return run(["open", url])
    if IS_WINDOWS:
        return _startfile(url)
    return f"Couldn't open {url} on this system."


def open_path(path: str) -> str:
    """Open a local file or folder with the OS default handler."""
    path = os.path.abspath(os.path.expanduser(path))
    if IS_LINUX and shutil.which("xdg-open"):
        try:
            subprocess.Popen(["xdg-open", path], stdout=subprocess.DEVNULL,
                             stderr=subprocess.DEVNULL, start_new_session=True)
            return f"Opened: {path}"
        except OSError as e:
            return f"Error: {e}"
    if IS_MACOS:
        res = run(["open", path])
        return f"Opened: {path}" if res == "Success" else res
    if IS_WINDOWS:
        res = _startfile(path)
        return f"Opened: {path}" if res == "Success" else res
    return f"Couldn't open {path} on this system."


def copy_to_clipboard(text: str) -> str:
    """Copy text to the system clipboard (desktop form of 'share')."""
    return clipboard_set(text)


def download_file(url: str, title: str = "Download") -> str:
    """Download a file to ~/Downloads with the native HTTP client."""
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    name = re.sub(r"[^\w.-]", "_", title) or "download"
    prefix, _, suffix = url.rpartition(".")
    if prefix and suffix and len(suffix) <= 5:
        name += f".{suffix}"
    dest = os.path.join(DOWNLOAD_DIR, name)

    if IS_WINDOWS:
        script = (f"Invoke-WebRequest -Uri '{url}' -OutFile '{dest}' "
                  f"-UseBasicParsing; Write-Output 'Success'")
        res = powershell(script, timeout=300)
        return f"Downloaded to {dest}" if res == "Success" else res

    for binary in ("wget", "curl"):
        if shutil.which(binary):
            argv = ([binary, "-q", "-O", dest, url] if binary == "wget"
                    else [binary, "-sSL", "-o", dest, url])
            res = run(argv, timeout=300)
            if not res.startswith("Error") and os.path.exists(dest):
                return f"Downloaded to {dest}"
            return res
    return "Error: neither wget nor curl is installed."
