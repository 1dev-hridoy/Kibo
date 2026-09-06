"""
Process and app control tools.
Focus, minimize, maximize, close, type text, send hotkeys.
"""

import subprocess
import os
import time


def _run_cmd(cmd, timeout=5):
    """Run a shell command and return output."""
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=timeout
        )
        return result.stdout.strip(), result.returncode
    except subprocess.TimeoutExpired:
        return "Command timed out", 1
    except Exception as e:
        return str(e), 1


def _find_window_by_name(name):
    """Find window ID by app name using xdotool."""
    from agent.config import IS_LINUX
    if not IS_LINUX:
        return None

    # Try xdotool search
    output, code = _run_cmd(f'xdotool search --name "{name}" 2>/dev/null')
    if code == 0 and output:
        return output.split("\n")[0]
    return None


def focus_app(name):
    """Bring an app window to the front."""
    from agent.config import IS_LINUX, IS_WINDOWS, IS_MACOS

    wid = _find_window_by_name(name)
    if wid:
        _run_cmd(f'xdotool windowactivate {wid} 2>/dev/null')
        _run_cmd(f'xdotool windowfocus {wid} 2>/dev/null')
        return f"Focused: {name} (window {wid})"

    # Try wmctrl
    output, code = _run_cmd(f'wmctrl -a "{name}" 2>/dev/null')
    if code == 0:
        return f"Focused: {name}"

    return f"Could not find window: {name}"


def minimize_app(name):
    """Minimize an app window."""
    wid = _find_window_by_name(name)
    if wid:
        _run_cmd(f'xdotool windowminimize {wid} 2>/dev/null')
        return f"Minimized: {name}"

    output, code = _run_cmd(f'wmctrl -r "{name}" -b add,hidden 2>/dev/null')
    if code == 0:
        return f"Minimized: {name}"

    return f"Could not find window: {name}"


def maximize_app(name):
    """Maximize an app window."""
    wid = _find_window_by_name(name)
    if wid:
        _run_cmd(f'xdotool windowactivate {wid} 2>/dev/null')
        _run_cmd(f'wmctrl -i -r {wid} -b add,maximized_vert,maximized_horz 2>/dev/null')
        return f"Maximized: {name}"

    return f"Could not find window: {name}"


def close_app(name):
    """Close an app window."""
    wid = _find_window_by_name(name)
    if wid:
        _run_cmd(f'xdotool windowclose {wid} 2>/dev/null')
        return f"Closed: {name} (window {wid})"

    # Try wmctrl
    output, code = _run_cmd(f'wmctrl -c "{name}" 2>/dev/null')
    if code == 0:
        return f"Closed: {name}"

    # Try pkill as last resort
    output, code = _run_cmd(f'pkill -f "{name}" 2>/dev/null')
    if code == 0:
        return f"Killed process: {name}"

    return f"Could not close: {name}"


def type_in_app(name, text):
    """Type text into a focused app window."""
    # First focus the app
    focus_result = focus_app(name)
    time.sleep(0.2)

    # Type the text using xdotool
    from agent.config import IS_LINUX
    if IS_LINUX:
        # Escape special characters for xdotool
        escaped = text.replace('"', '\\"')
        _run_cmd(f'xdotool type --clearmodifiers "{escaped}" 2>/dev/null')
        return f"Typed in {name}: {text[:50]}..."

    return f"Type not supported on this platform"


def hotkey_in_app(name, keys):
    """Send keyboard shortcut to an app window.
    
    Keys format: "ctrl+c", "alt+tab", "ctrl+shift+t", etc.
    """
    # First focus the app
    focus_result = focus_app(name)
    time.sleep(0.2)

    # Send the hotkey using xdotool
    from agent.config import IS_LINUX
    if IS_LINUX:
        _run_cmd(f'xdotool key {keys} 2>/dev/null')
        return f"Sent {keys} to {name}"

    return f"Hotkey not supported on this platform"


def list_windows():
    """List all open windows."""
    from agent.config import IS_LINUX
    if IS_LINUX:
        output, code = _run_cmd('wmctrl -l 2>/dev/null')
        if code == 0 and output:
            windows = []
            for line in output.strip().split("\n"):
                parts = line.split(None, 3)
                if len(parts) >= 4:
                    windows.append({
                        "id": parts[0],
                        "title": parts[3],
                    })
            if windows:
                result = "Open windows:\n"
                for w in windows:
                    result += f"  - {w['title']} ({w['id']})\n"
                return result
        return "No windows found (wmctrl not available)"
    return "Window listing not supported on this platform"


def get_active_window():
    """Get the currently active/focused window."""
    from agent.config import IS_LINUX
    if IS_LINUX:
        output, code = _run_cmd('xdotool getactivewindow getwindowname 2>/dev/null')
        if code == 0 and output:
            return f"Active window: {output}"
        output, code = _run_cmd('wmctrl -a :ACTIVE: 2>/dev/null')
    return "Could not get active window"
