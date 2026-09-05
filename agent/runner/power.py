"""Power actions: power_action()."""

import shutil

from agent.config import IS_WINDOWS, IS_MACOS, IS_LINUX
from agent.runner.common import run, powershell


def power_action(action: str) -> str:
    """'shutdown' | 'restart' | 'sleep' | 'hibernate' (asks the OS politely)."""
    if IS_LINUX:
        argv = {"shutdown": ["systemctl", "poweroff"],
                "restart": ["systemctl", "reboot"],
                "sleep": ["systemctl", "suspend"],
                "hibernate": ["systemctl", "hibernate"]}.get(action)
        if not argv:
            return f"Unknown power action '{action}'."
        if not shutil.which("systemctl"):
            return "systemctl is not available on this system."
        res = run(argv, timeout=30)
        return {"shutdown": "Shutting down", "restart": "Restarting",
                "sleep": "Going to sleep", "hibernate": "Hibernating"}[action] \
            if not res.startswith("Error") else res
    if IS_MACOS:
        argv = {"shutdown": ["osascript", "-e",
                             'do shell script "shutdown -h now" with administrator privileges'],
                "restart": ["osascript", "-e",
                            'do shell script "shutdown -r now" with administrator privileges'],
                "sleep": ["pmset", "sleepnow"],
                "hibernate": ["pmset", "sleepnow"]}.get(action)
        if not argv:
            return f"Unknown power action '{action}'."
        return run(argv, timeout=60) or {"shutdown": "Shutting down",
                                         "restart": "Restarting",
                                         "sleep": "Going to sleep",
                                         "hibernate": "Sleeping"}[action]
    if IS_WINDOWS:
        argv = {"shutdown": ["shutdown", "/s", "/t", "5"],
                "restart": ["shutdown", "/r", "/t", "5"],
                "sleep": ["rundll32.exe", "powrprof.dll,SetSuspendState", "0,1,0"],
                "hibernate": ["rundll32.exe", "powrprof.dll,SetSuspendState", "0,1,0"]}.get(action)
        if not argv:
            return f"Unknown power action '{action}'."
        return run(argv, timeout=30) or {"shutdown": "Shutting down in 5s",
                                         "restart": "Restarting in 5s",
                                         "sleep": "Going to sleep",
                                         "hibernate": "Hibernating"}[action]
    return "Power actions are not supported on this system."
