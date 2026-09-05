"""
System tools — cross-platform: notifications, battery, clipboard,
brightness, volume, screen lock. Native backends for Linux, Windows
and macOS live in agent.runner.
"""

import needle
from agent.runner import (
    notify, toast, battery_status, clipboard_set, clipboard_get,
    set_brightness, volume_info, set_volume, lock_screen, system_stats,
)


@needle.tool
def show_toast(message: str):
    """Show a brief toast popup on the user's screen."""
    print(f"[Tool] show_toast('{message}')")
    return toast(message)


@needle.tool
def show_notification(title: str, message: str = ""):
    """Show a persistent desktop notification with a title and body."""
    print(f"[Tool] show_notification('{title}')")
    return notify(title, message)


@needle.tool
def get_battery_status():
    """Get battery level and charging status (laptops only)."""
    print("[Tool] get_battery_status()")
    info = battery_status()
    if info is None:
        return "This PC has no battery — it's running on AC power."
    pct = info.get("percent", "?")
    status = info.get("status", "unknown").lower()
    temp = info.get("temperature")
    temp_s = f", temp {temp}C" if temp is not None else ""
    return f"Battery: {pct}% ({status}{temp_s})"


@needle.tool
def set_clipboard(text: str):
    """Copy text to the system clipboard."""
    print(f"[Tool] set_clipboard('{text[:30]}')")
    return clipboard_set(text)


@needle.tool
def get_clipboard():
    """Read the current text content of the system clipboard."""
    print("[Tool] get_clipboard()")
    return clipboard_get()


@needle.tool
def set_screen_brightness(level: int):
    """Set screen brightness: 0-100 (percent) or 0-255 (raw)."""
    print(f"[Tool] set_screen_brightness({level})")
    return set_brightness(level)


@needle.tool
def get_volume_info():
    """Get current audio output volume levels."""
    print("[Tool] get_volume_info()")
    vols = volume_info()
    if not vols:
        return "Couldn't read the audio output volume on this system."
    parts = ", ".join(f"{v['stream']}: {v['volume']}/{v['max_volume']}"
                      for v in vols)
    return f"Volume — {parts}"


@needle.tool
def set_volume(level: int, stream: str = "music"):
    """Set the audio output volume (0-100)."""
    print(f"[Tool] set_volume({level})")
    from agent.runner import set_volume as _set
    return _set(stream, level)


@needle.tool
def lock_the_screen():
    """Lock the screen / workstation so a password is required."""
    print("[Tool] lock_the_screen()")
    return lock_screen()


@needle.tool
def get_system_stats():
    """Get CPU load and RAM usage for this PC."""
    print("[Tool] get_system_stats()")
    stats = system_stats()
    if not stats:
        return "Couldn't read CPU or memory usage on this system."
    parts = []
    if "cpu_percent" in stats:
        parts.append(f"CPU {stats['cpu_percent']}%")
    if "load1" in stats:
        parts.append(f"load {stats['load1']}")
    if "mem_percent" in stats:
        parts.append(f"RAM {stats['mem_used_gb']}/{stats['mem_total_gb']} GB "
                     f"({stats['mem_percent']}%)")
    return ", ".join(parts) if parts else "No CPU/RAM data available."
