"""File management: list_files(), list_installed_apps(), file_create(), file_delete(), file_move(), file_read()."""

import json
import os
import shutil

from agent.config import IS_WINDOWS, IS_MACOS, IS_LINUX, HOME
from agent.runner.common import run, powershell


def list_files(path: str = "") -> dict:
    """List files and folders in a directory. Returns {path, items: [{name, type, size}]}."""
    target = os.path.expanduser(path) if path else HOME
    target = os.path.abspath(target)
    if not os.path.isdir(target):
        return {"error": f"Not a directory: {target}", "path": target, "items": []}
    items = []
    try:
        for entry in sorted(os.listdir(target)):
            full = os.path.join(target, entry)
            is_dir = os.path.isdir(full)
            size = 0
            try:
                size = os.path.getsize(full) if not is_dir else 0
            except OSError:
                pass
            items.append({
                "name": entry,
                "type": "dir" if is_dir else "file",
                "size": size,
            })
    except PermissionError:
        return {"error": "Permission denied", "path": target, "items": []}
    return {"path": target, "items": items[:100], "total": len(items)}


def list_installed_apps() -> list:
    """Return a list of installed applications on this system."""
    apps = []
    if IS_LINUX:
        # Try pacman first (Arch), then dpkg (Debian/Ubuntu), then rpm
        if shutil.which("pacman"):
            out = run(["pacman", "-Q"], timeout=10)
            if not out.startswith("Error"):
                for line in out.splitlines():
                    parts = line.split()
                    if len(parts) >= 2:
                        apps.append({"name": parts[0], "version": parts[1]})
        elif shutil.which("dpkg-query"):
            out = run(["dpkg-query", "-W", "-f", "${Package}\t${Version}\n"], timeout=15)
            if not out.startswith("Error"):
                for line in out.splitlines():
                    parts = line.split("\t")
                    if len(parts) >= 2:
                        apps.append({"name": parts[0], "version": parts[1]})
        elif shutil.which("rpm"):
            out = run(["rpm", "-qa", "--queryformat", "%{NAME}\t%{VERSION}\n"], timeout=15)
            if not out.startswith("Error"):
                for line in out.splitlines():
                    parts = line.split("\t")
                    if len(parts) >= 2:
                        apps.append({"name": parts[0], "version": parts[1]})
        elif shutil.which("snap"):
            out = run(["snap", "list"], timeout=10)
            if not out.startswith("Error"):
                for line in out.splitlines()[1:]:  # skip header
                    parts = line.split()
                    if len(parts) >= 2:
                        apps.append({"name": parts[0], "version": parts[1]})
    elif IS_MACOS:
        out = run(["ls", "/Applications"], timeout=10)
        if not out.startswith("Error"):
            for name in out.splitlines():
                if name.endswith(".app"):
                    apps.append({"name": name[:-4], "version": ""})
    elif IS_WINDOWS:
        script = '''
$apps = @()
$paths = @(
    "${env:ProgramFiles}\\*",
    "${env:ProgramFiles(x86)}\\*",
    "${env:LOCALAPPDATA}\\*"
)
foreach ($p in $paths) {
    if (Test-Path $p) {
        Get-ChildItem $p -Directory -ErrorAction SilentlyContinue | ForEach-Object {
            $apps += "$($_.Name)"
        }
    }
}
$apps | Sort-Object -Unique | Select-Object -First 200
'''
        out = powershell(script, timeout=30)
        if not out.startswith("Error"):
            for name in out.splitlines():
                name = name.strip()
                if name:
                    apps.append({"name": name, "version": ""})
    return apps[:500]


def file_create(path: str, content: str = "") -> str:
    """Create a file with optional content."""
    path = os.path.expanduser(path)
    try:
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        with open(path, "w") as f:
            f.write(content)
        return f"Created: {path}"
    except OSError as e:
        return f"Error: {e}"


def file_delete(path: str) -> str:
    """Delete a file or empty directory."""
    path = os.path.expanduser(path)
    if not os.path.exists(path):
        return f"Not found: {path}"
    try:
        if os.path.isdir(path):
            os.rmdir(path)
            return f"Deleted directory: {path}"
        else:
            os.remove(path)
            return f"Deleted file: {path}"
    except OSError as e:
        return f"Error: {e}"


def file_move(src: str, dst: str) -> str:
    """Move/rename a file or directory."""
    src = os.path.expanduser(src)
    dst = os.path.expanduser(dst)
    if not os.path.exists(src):
        return f"Not found: {src}"
    try:
        shutil.move(src, dst)
        return f"Moved: {src} -> {dst}"
    except OSError as e:
        return f"Error: {e}"


def file_read(path: str, lines: int = 50) -> str:
    """Read the last N lines of a file (for logs, configs, etc)."""
    path = os.path.expanduser(path)
    if not os.path.exists(path):
        return f"Not found: {path}"
    try:
        with open(path, "r", errors="replace") as f:
            all_lines = f.readlines()
        tail = all_lines[-lines:] if len(all_lines) > lines else all_lines
        return "".join(tail)
    except OSError as e:
        return f"Error: {e}"
