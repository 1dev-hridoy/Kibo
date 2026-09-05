"""
Hardware & power tools — cross-platform: device identity, screenshots,
screen lock, shutdown / restart / sleep.
"""

import needle
from agent.runner import (
    device_info, take_screenshot, lock_screen, power_action,
)


@needle.tool
def get_device_info():
    """Get this PC's model, operating system and hostname."""
    print("[Tool] get_device_info()")
    info = device_info()
    model = info.get("model") or "Unknown PC"
    os_name = info.get("os") or "unknown OS"
    serial = info.get("serial")
    serial_s = f" (host: {serial})" if serial else ""
    return f"This is a {model} running {os_name}{serial_s}."


@needle.tool
def take_screenshot_now():
    """Capture the screen and save the image to the Downloads folder."""
    print("[Tool] take_screenshot_now()")
    return take_screenshot()


@needle.tool
def lock_screen_now():
    """Lock the screen / workstation so a password is required."""
    print("[Tool] lock_screen_now()")
    return lock_screen()


@needle.tool
def power_control(action: str):
    """Shut down, restart, sleep or hibernate the PC.
    action: 'shutdown', 'restart', 'sleep' or 'hibernate'."""
    print(f"[Tool] power_control('{action}')")
    return power_action(action.lower().strip())
