import os
import platform
import sys

APP_NAME = "kibo"


def _linux_desktop_path():
    base = os.path.expanduser("~/.config/autostart")
    os.makedirs(base, exist_ok=True)
    return os.path.join(base, "kibo.desktop")


def _mac_plist_path():
    base = os.path.expanduser("~/Library/LaunchAgents")
    os.makedirs(base, exist_ok=True)
    return os.path.join(base, "com.kibo.agent.plist")


def _windows_startup_path():
    base = os.path.join(
        os.environ.get("APPDATA", ""),
        "Microsoft", "Windows", "Start Menu", "Programs", "Startup",
    )
    os.makedirs(base, exist_ok=True)
    return os.path.join(base, "kibo.bat")


def _launch_cmd():
    py = sys.executable
    return f'"{py}" -m agent web'






def enable():
    system = platform.system()
    if system == "Linux":
        with open(_linux_desktop_path(), "w") as f:
            f.write(
                "[Desktop Entry]\n"
                "Type=Application\n"
                "Name=Kibo\n"
                f"Exec={_launch_cmd()}\n"
                "X-GNOME-Autostart-enabled=true\n"
                "Terminal=false\n"
            )
        return f"Autostart enabled: {_linux_desktop_path()}"
    if system == "Darwin":
        with open(_mac_plist_path(), "w") as f:
            f.write(
                '<?xml version="1.0" encoding="UTF-8"?>\n'
                '<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" '
                '"http://www.apple.com/DTDs/PropertyList-1.0.dtd">\n'
                '<plist version="1.0"><dict>\n'
                "<key>Label</key><string>com.kibo.agent</string>\n"
                "<key>ProgramArguments</key><array>\n"
                f"<string>{sys.executable}</string>\n"
                "<string>-m</string><string>agent</string><string>web</string>\n"
                "</array>\n"
                "<key>RunAtLoad</key><true/>\n"
                "</dict></plist>\n"
            )
        return f"Autostart enabled: {_mac_plist_path()}"
    if system == "Windows":
        with open(_windows_startup_path(), "w") as f:
            f.write(f"@echo off\n{_launch_cmd()}\n")
        return f"Autostart enabled: {_windows_startup_path()}"
    return f"Autostart not supported on {system}"




def disable():
    removed = []
    for path in (_linux_desktop_path(), _mac_plist_path(),
                 _windows_startup_path()):
        try:
            if os.path.exists(path):
                os.remove(path)
                removed.append(path)
        except OSError:
            pass
    if removed:
        return "Autostart disabled: " + ", ".join(removed)
    return "Autostart was not enabled"







def status():
    system = platform.system()
    if system == "Linux":
        p = _linux_desktop_path()
    elif system == "Darwin":
        p = _mac_plist_path()
    elif system == "Windows":
        p = _windows_startup_path()
    else:
        return f"Autostart not supported on {system}"
    if os.path.exists(p):
        return f"Autostart is ENABLED ({p})"
    return "Autostart is DISABLED"





def is_enabled():
    system = platform.system()
    if system == "Linux":
        return os.path.exists(_linux_desktop_path())
    if system == "Darwin":
        return os.path.exists(_mac_plist_path())
    if system == "Windows":
        return os.path.exists(_windows_startup_path())
    return False
