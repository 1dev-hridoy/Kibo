"""
Live screen viewing for the Web UI.
Provides periodic screenshot refresh for remote viewing.
"""

import os
import time
import threading


def take_screenshot():
    """Take a screenshot and return the path."""
    from agent.runner.screen import take_screenshot
    result = take_screenshot()

  
    if "Screenshot saved to" in result:
        return result.split("Screenshot saved to ")[1].strip()
    return None


def get_screen_info():
    """Get current screen resolution and info."""
    try:
        import subprocess
        output = subprocess.run(
            ["xrandr"], capture_output=True, text=True, timeout=3
        ).stdout
        for line in output.split("\n"):
            if "*" in line:
                return line.strip()
        return "Unknown resolution"
    except Exception:
        return "Unknown resolution"



_screenshot_cache = {"path": None, "timestamp": 0}
_cache_lock = threading.Lock()
CACHE_DURATION = 2 


def get_latest_screenshot(force=False):
    """Get the latest screenshot, using cache to avoid too many captures."""
    global _screenshot_cache
    with _cache_lock:
        now = time.time()
        if not force and _screenshot_cache["path"] and \
           (now - _screenshot_cache["timestamp"]) < CACHE_DURATION:
            return _screenshot_cache["path"]

        path = take_screenshot()
        if path and os.path.exists(path):
            _screenshot_cache["path"] = path
            _screenshot_cache["timestamp"] = now
            return path
        return _screenshot_cache.get("path")
