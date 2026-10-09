import os
import platform
import shutil
import subprocess
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


def _repo_root():
    return os.path.dirname(os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))))




def _unit_path():
    base = os.path.expanduser("~/.config/systemd/user")
    os.makedirs(base, exist_ok=True)
    return os.path.join(base, "kibo.service")




def _systemd_available():
    return (platform.system() == "Linux"
            and shutil.which("systemctl") is not None)




def _systemctl(*args):
    try:
        return subprocess.run(["systemctl", "--user", *args],
                              
                              capture_output=True, text=True, timeout=20)


    
    except Exception as e:
        print(f"[Autostart] systemctl {' '.join(args)}: {e}")
        return None


def _write_unit():
    py = sys.executable


    unit = (
        "[Unit]\n"
        "Description=Kibo assistant (web + telegram + widget)\n"
        "After=graphical-session.target\n"
        "\n"
        "[Service]\n"
        "Type=simple\n"
        f"WorkingDirectory={_repo_root()}\n"
        f'ExecStart="{py}" -m agent all\n'
        "Environment=PYTHONUNBUFFERED=1\n"
        "Restart=on-failure\n"
        "RestartSec=5\n"
        "\n"
        "[Install]\n"
        "WantedBy=graphical-session.target\n"
    )



    with open(_unit_path(), "w") as f:
        f.write(unit)


def _systemd_enabled():
    if not os.path.exists(_unit_path()):
        return False
    r = _systemctl("is-enabled", "kibo.service")
    if not r:
        return False
    return (r.stdout or "").strip() == "enabled"


def _launch_cmd():
    py = sys.executable
    return f'"{py}" -m agent all'


def enable():
    system = platform.system()
    if system == "Linux":


     
        if _systemd_available():
            try:
                _write_unit()
            except OSError as e:
                return f"Could not write service unit: {e}"
            _systemctl("daemon-reload")
            r = _systemctl("enable", "kibo.service")


            if r is None or r.returncode != 0:
                err = ((r.stderr or r.stdout or "").strip() if r
                       else "systemctl not available")
                return f"Autostart failed: {err}"

            
            try:
                if os.path.exists(_linux_desktop_path()):
                    os.remove(_linux_desktop_path())
            except OSError:
                pass
            return (f"Autostart ENABLED (systemd user service kibo.service)\n"
                    f"Unit: {_unit_path()}\n"
                    f"Kibo (web + telegram + widget) starts at next "
                    f"login / boot.")
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
                "<string>-m</string><string>agent</string>"
                "<string>all</string>\n"
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
    if _systemd_available() and (
            os.path.exists(_unit_path())
            or _systemd_enabled()):
        _systemctl("disable", "kibo.service")
        try:
            if os.path.exists(_unit_path()):
                os.remove(_unit_path())
                removed.append(_unit_path())
        except OSError:
            pass
        _systemctl("daemon-reload")
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
        if _systemd_available() and os.path.exists(_unit_path()):
            if _systemd_enabled():
                return ("Autostart is ENABLED via systemd user service "
                        "(kibo.service) — Kibo starts at login/boot.")
            return ("Autostart is DISABLED (kibo.service exists but is "
                    "not enabled).")
        if os.path.exists(_linux_desktop_path()):
            return f"Autostart is ENABLED ({_linux_desktop_path()})"
        return "Autostart is DISABLED"
    if system == "Darwin":
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
        if _systemd_available() and os.path.exists(_unit_path()):
            return _systemd_enabled()
        return os.path.exists(_linux_desktop_path())
    if system == "Darwin":
        return os.path.exists(_mac_plist_path())
    if system == "Windows":
        return os.path.exists(_windows_startup_path())
    return False
