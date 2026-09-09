"""
System administration tools — process management, file operations,
disk monitoring, log viewing, package management.
"""

import shutil
import subprocess

import needle
from agent.config import IS_WINDOWS, IS_LINUX, IS_MACOS, LINUX_DISTRO
from agent.runner import (
    list_processes, kill_process,
    file_create, file_delete, file_move, file_read,
    disk_usage, system_temperature,
    view_logs, package_install, package_uninstall,
)


def _sandbox_check(path: str):
    """Lazy import of sandbox to avoid circular imports."""
    from agent.core.sandbox import validate_write_path, SandboxError
    try:
        validate_write_path(path)
    except SandboxError as e:
        return str(e)
    return None


# ═══════════════════════════════════════════════════════════════════════
# Process management
# ═══════════════════════════════════════════════════════════════════════

@needle.tool
def get_running_processes(filter_name: str = ""):
    """List running processes on this PC. Optionally filter by name (e.g. 'python', 'chrome')."""
    print(f"[Tool] get_running_processes('{filter_name}')")
    procs = list_processes(filter_name)
    if not procs:
        return "No running processes found."
    lines = [f"Top processes (by CPU):"]
    for p in procs[:20]:
        lines.append(f"  PID {p['pid']}: {p['command'][:60]} (CPU {p['cpu']}%, MEM {p['mem']}%)")
    if len(procs) > 20:
        lines.append(f"  ... and {len(procs) - 20} more")
    return "\n".join(lines)


@needle.tool
def kill_a_process(pid: int):
    """Kill a running process by its PID number."""
    print(f"[Tool] kill_a_process({pid})")
    return kill_process(pid)


# ═══════════════════════════════════════════════════════════════════════
# File management
# ═══════════════════════════════════════════════════════════════════════

@needle.tool
def create_file(path: str, content: str = ""):
    """Create a new file with optional content."""
    print(f"[Tool] create_file('{path}')")
    err = _sandbox_check(path)
    if err:
        return err
    return file_create(path, content)


@needle.tool
def delete_file(path: str):
    """Delete a file or empty directory."""
    print(f"[Tool] delete_file('{path}')")
    err = _sandbox_check(path)
    if err:
        return err
    return file_delete(path)


@needle.tool
def move_file(source: str, destination: str):
    """Move or rename a file/folder."""
    print(f"[Tool] move_file('{source}', '{destination}')")
    err = _sandbox_check(source) or _sandbox_check(destination)
    if err:
        return err
    return file_move(source, destination)


@needle.tool
def read_file(path: str, lines: int = 50):
    """Read the contents of a file (last N lines). Useful for logs, configs, text files."""
    print(f"[Tool] read_file('{path}', {lines})")
    return file_read(path, lines)


# ═══════════════════════════════════════════════════════════════════════
# Disk & temperature
# ═══════════════════════════════════════════════════════════════════════

@needle.tool
def get_disk_usage():
    """Show disk space usage for all drives/partitions."""
    print("[Tool] get_disk_usage()")
    disks = disk_usage()
    if not disks:
        return "Couldn't read disk usage."
    lines = ["Disk usage:"]
    for d in disks:
        lines.append(f"  {d['device']} ({d['mount']}): {d['used']}/{d['total']} ({d['percent']} used) — {d['available']} free")
    return "\n".join(lines)


@needle.tool
def get_temperature():
    """Read CPU/system temperature sensors."""
    print("[Tool] get_temperature()")
    temps = system_temperature()
    if not temps:
        return "No temperature sensors detected on this system."
    lines = ["Temperature sensors:"]
    for name, temp in temps.items():
        lines.append(f"  {name}: {temp}°C")
    return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════════════
# Log viewer
# ═══════════════════════════════════════════════════════════════════════

@needle.tool
def view_system_logs(log_type: str = "system", lines: int = 30, grep: str = ""):
    """View system logs. Types: 'system', 'auth', 'kernel', 'journal', or a file path.
    Optionally filter with grep keyword."""
    print(f"[Tool] view_system_logs('{log_type}', {lines}, '{grep}')")
    return view_logs(log_type, lines, grep)


# ═══════════════════════════════════════════════════════════════════════
# Package management
# ═══════════════════════════════════════════════════════════════════════

@needle.tool
def install_package(name: str):
    """Install software package (uses pacman/apt/dnf/brew/winget)."""
    print(f"[Tool] install_package('{name}')")
    return package_install(name)


@needle.tool
def uninstall_package(name: str):
    """Uninstall a software package."""
    print(f"[Tool] uninstall_package('{name}')")
    return package_uninstall(name)


# ═══════════════════════════════════════════════════════════════════════
# System Health Check
# ═══════════════════════════════════════════════════════════════════════

# Required dependencies per platform
_LINUX_DEPS = {
    "notify-send": "libnotify",
    "brightnessctl": "brightnessctl",
    "nmcli": "network-manager",
    "wl-copy": "wl-clipboard",
    "xclip": "xclip",
    "grim": "grim",
    "scrot": "scrot",
    "espeak-ng": "espeak-ng",
    "ffmpeg": "ffmpeg",
    "nmap": "nmap",
}



_MACOS_DEPS = {
    "ffmpeg": "ffmpeg",
    "nmap": "nmap",
}

_WINDOWS_DEPS = {
    "nmap": "nmap",
}




@needle.tool
def check_system_health(auto_install: bool = False) -> str:
    """Diagnose system dependencies and check if required tools are installed.
    Set auto_install=True to automatically install missing packages.
    Shows: platform info, installed tools, missing tools, Python version."""
    print(f"[Tool] check_system_health(auto_install={auto_install})")

    lines = ["=== Kibo System Health Report ===\n"]

    # Platform info
    import platform
    lines.append(f"Platform: {platform.system()} {platform.release()}")
    lines.append(f"Python: {platform.python_version()}")
    lines.append(f"Architecture: {platform.machine()}")

    if IS_LINUX:
        lines.append(f"Linux Distro: {LINUX_DISTRO or 'unknown'}")
    lines.append("")




  
    lines.append("--- Python Packages ---")
    py_packages = {
        "flask": "Flask",
        "pydantic": "Pydantic",
        "requests": "Requests",
        "dotenv": "python-dotenv",
        "needle": "cactus-needle",
    }
    for module, name in py_packages.items():
        try:
            __import__(module)
            lines.append(f"  [OK] {name}")
        except ImportError:
            lines.append(f"  [MISSING] {name}")

    lines.append("")





    lines.append("--- System Dependencies ---")
    if IS_LINUX:
        deps = _LINUX_DEPS
    elif IS_MACOS:
        deps = _MACOS_DEPS
    elif IS_WINDOWS:
        deps = _WINDOWS_DEPS
    else:
        deps = {}

    missing = []
    for binary, package in deps.items():
        found = shutil.which(binary)
        if found:
            lines.append(f"  [OK] {binary}")
        else:
            lines.append(f"  [MISSING] {binary} (package: {package})")
            missing.append(package)




    lines.append("\n--- Optional Extras ---")
    optional = {
        "mpv": "Media player (mpv)",
        "git": "Version control (git)",
        "curl": "HTTP client (curl)",
        "wget": "Download tool (wget)",
    }
    for binary, desc in optional.items():
        found = shutil.which(binary)
        status = "[OK]" if found else "[NOT FOUND]"
        lines.append(f"  {status} {desc}")





  
    if auto_install and missing:
        lines.append(f"\n--- Auto-Installing {len(missing)} missing packages ---")
        for pkg in missing:
            result = package_install(pkg)
            if result.startswith("Error"):
                lines.append(f"  [FAIL] {pkg}: {result}")
            else:
                lines.append(f"  [INSTALLED] {pkg}")
    elif missing:
        lines.append(f"\n{len(missing)} missing packages. Run with auto_install=True to install them.")

    lines.append("\n=== Health Check Complete ===")
    return "\n".join(lines)
