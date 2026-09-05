"""
Deterministic fast-path routing for simple PC commands.
"""

import re

_last_topic = None


def _num(text, before, after):
    """First 0-100 integer sitting between the two keyword patterns."""
    m = (re.search(before + rf"[^\d%]{{0,24}}(\d{{1,3}})\s*%?", text)
         or re.search(rf"(\d{{1,3}})\s*%?[^\d]{{0,24}}" + after, text))
    return int(m.group(1)) if m and 0 <= int(m.group(1)) <= 100 else None


def _fastpath(text):
    """Map simple device commands straight to tool calls.

    Returns a list of (tool_name, args) tuples, or None to defer to
    the model. Info queries route through here too so answers are
    always well-formatted.
    """
    global _last_topic
    t = text.lower().strip()

    # ── Model management commands ──────────────────────────────────────
    m = re.match(r"^(?:switch|change|use)\s+(?:to\s+)?(?:model\s+)?(\w+)[.!?]?$", t)
    if m:
        return "__switch_model__", m.group(1).lower()

    if re.match(r"^(?:needle|needle2|n|gemma|google|func|functiongemma|fg)[.!?]?$", t):
        return "__switch_model__", t.rstrip(".")

    if re.match(r"^(?:models?|model status|which model|what model|list models?)[.!?]?$", t):
        return "__models__", None

    if re.match(r"^(?:current|active|what|which)\s+model\s*(?:am\s+i\s+using|name)?[.!?]?$", t):
        return "__current_model__", None

    # follow-up: "make it 50" / "set it to 50" / "make it 50%"
    if _last_topic in ("volume", "brightness"):
        m = re.match(r"^(?:make|set|turn|change|put)\s+(?:it|that|the \w+)?\s*"
                     r"(?:to)?\s*(\d{1,3})\s*%?[.!?]?$", t)
        if m and 0 <= int(m.group(1)) <= 100:
            n = int(m.group(1))
            if _last_topic == "volume":
                return [("set_volume", {"stream": "music", "level": n})]
            return [("set_screen_brightness", {"level": n})]

    # ── SYSTEM CONTROLS ────────────────────────────────────────────────

    # brightness
    if re.search(r"\b(brightness|brighter|dim|dimmer)\b", t):
        n = _num(t, r"\b(?:brightness|brighter|dimmer?|screen)\b",
                 r"\bbrightness\b")
        if n is not None:
            return [("set_screen_brightness", {"level": n})]

    # volume / sound / speaker level
    vol = re.search(r"\b(volume|sound|speaker|audio)\b", t)
    mentions_brightness = bool(re.search(r"\bbrightness\b", t))
    if re.search(r"\bmute\b", t) and "unmute" not in t:
        return [("set_volume", {"stream": "music", "level": 0})]
    if re.search(r"\bunmute\b", t):
        return [("set_volume", {"stream": "music", "level": 60})]
    n = (_num(t, r"\b(?:volume|sound|speaker|audio)\b",
              r"\b(?:volume|sound|speaker)") if vol else None)
    if n is None and vol and re.search(r"\b(max|full|highest|loudest)\b", t):
        n = 100
    directional = bool(re.search(
        r"\b(louder|turn up|turn it up|crank|increase|"
        r"quieter|turn down|turn it down|lower)\b", t))
    if (n is None and directional and not mentions_brightness
            and _last_topic != "brightness"):
        n = 90 if re.search(r"\b(louder|turn up|turn it up|crank|increase)\b", t) else 30
    if n is None and vol and not mentions_brightness:
        if re.search(r"\b(up|louder|increase|higher)\b", t):
            n = 90
        elif re.search(r"\b(down|quieter|decrease|lower)\b", t):
            n = 30
    if n is not None and (vol or directional):
        return [("set_volume", {"stream": "music", "level": n})]
    if vol and re.search(r"\b(what|how|current|get|show|check|level)\b", t):
        return [("get_volume_info", {})]

    # PC actions
    if re.search(r"\b(screenshot|screen ?shot|capture (?:the |my )?screen)\b", t):
        return [("take_screenshot_now", {})]
    if re.search(r"\block\b", t) and re.search(
            r"\b(screen|pc|computer|workstation|session)\b", t):
        return [("lock_screen_now", {})]
    if re.search(r"\b(shut ?down|power ?off|turn off (?:the |my )?(?:pc|computer))\b", t):
        return [("power_control", {"action": "shutdown"})]
    if re.search(r"\b(restart|reboot)\b", t):
        return [("power_control", {"action": "restart"})]
    if re.search(r"\b(?:put (?:the |my )?(?:pc|computer) (?:to )?sleep|suspend)\b", t):
        return [("power_control", {"action": "sleep"})]

    # ── INFO QUERIES ───────────────────────────────────────────────────

    if re.search(r"\bbattery\b", t):
        return [("get_battery_status", {})]
    if re.search(r"\b(cpu|ram|memory)\b", t) and re.search(
            r"\b(usage|used|load|how much|percent|stats?|utilization)\b", t):
        return [("get_system_stats", {})]
    if re.search(r"\b(wi-?fi|networks?)\b", t) and re.search(
            r"\b(scan|nearby|around|available|list)\b", t):
        return [("scan_wifi_networks", {})]
    if re.search(r"\b(wi-?fi|networks?|ssid|internet)\b", t):
        return [("get_wifi_info", {})]
    if re.search(r"\b(device info|system info|specs?\b|my (pc|computer|device|machine)|"
                 r"what (pc|computer|device|machine))", t):
        return [("get_device_info", {})]

    # clock / date
    if re.search(r"\b(time|clock|hour)\b", t) and re.search(
            r"\b(what|whats|tell|current|now|is it)\b", t):
        return "clock"
    if re.search(r"\b(date|day|today)\b", t) and re.search(
            r"\b(what|whats|tell|current|now|is it)\b", t):
        return "date"

    # ── FILE & FOLDER OPERATIONS ───────────────────────────────────────

    # "view downloads", "show downloads", "open downloads", "list downloads"
    m = re.match(r"^(?:view|show|open|list|browse|check|see)\s+(?:my\s+)?(?:the\s+)?downloads?[.!?]?$", t)
    if m:
        return [("list_files", {"path": "~/Downloads"})]

    # "view <folder>", "show <folder>", "open <folder>"
    m = re.match(r"^(?:view|show|open|list|browse|check|see)\s+(?:my\s+)?(?:the\s+)?(\w+(?:\s+\w+)?)\s+(?:folder|directory|files?|contents?)[.!?]?$", t)
    if m:
        folder = m.group(1).strip()
        folder_map = {
            "home": "~", "desktop": "~/Desktop", "documents": "~/Documents",
            "downloads": "~/Downloads", "pictures": "~/Pictures",
            "music": "~/Music", "videos": "~/Videos", "projects": "~/Projects",
        }
        path = folder_map.get(folder, f"~/{folder}")
        return [("list_files", {"path": path})]

    # "what's in <folder>", "what is in <folder>"
    m = re.match(r"^(?:what'?s|what is|what are)\s+in\s+(?:my\s+)?(?:the\s+)?(\w+(?:\s+\w+)?)[.!?]?$", t)
    if m:
        folder = m.group(1).strip()
        folder_map = {
            "home": "~", "desktop": "~/Desktop", "documents": "~/Documents",
            "downloads": "~/Downloads", "pictures": "~/Pictures",
            "music": "~/Music", "videos": "~/Videos", "projects": "~/Projects",
        }
        path = folder_map.get(folder, f"~/{folder}")
        return [("list_files", {"path": path})]

    # "open <folder>" (not app)
    m = re.match(r"^open\s+(?:my\s+)?(?:the\s+)?(downloads?|documents?|desktop|pictures?|music|videos?|projects?|home)[.!?]?$", t)
    if m:
        folder = m.group(1).strip()
        folder_map = {
            "home": "~", "desktop": "~/Desktop", "documents": "~/Documents",
            "downloads": "~/Downloads", "pictures": "~/Pictures",
            "music": "~/Music", "videos": "~/Videos", "projects": "~/Projects",
        }
        path = folder_map.get(folder, f"~/{folder}")
        return [("list_files", {"path": path})]

    # "list files" / "show files" / "browse files"
    if re.search(r"\b(list|show|browse|explore|ls|dir)\b", t) and re.search(
            r"\b(files?|folder|directories|contents|dir)\b", t):
        if not re.search(r"\btool", t):
            m = re.search(r"(?:in|at|from|of)\s+[\"']?([/~\w.\- ]+)[\"']?", t)
            path = m.group(1).strip() if m else ""
            return [("list_files", {"path": path})]

    # "read file <path>", "cat <path>", "show file <path>"
    m = re.search(r"\b(read|open|cat|view|show)\s+(?:the\s+)?file\s+[\"']?([/~\w.\- ]+)[\"']?", t)
    if m:
        return [("read_file", {"path": m.group(1).strip()})]

    # "installed apps" / "what apps" / "list programs"
    if re.search(r"\b(list|show|what|which)\b", t) and re.search(
            r"\b(installed|apps?|software|packages?|programs?)\b", t):
        if not re.search(r"\btool", t):
            return [("list_installed_apps", {})]

    # ── PROCESSES ──────────────────────────────────────────────────────

    # "kill process 1234" / "kill pid 1234" / "end process 1234"
    m = re.search(r"\b(kill|stop|terminate|end)\s+(?:the\s+)?(?:process|pid|task)\s*(\d+)", t)
    if m:
        return [("kill_a_process", {"pid": int(m.group(2))})]

    # "processes" / "running processes" / "what's running" / "tasks"
    if re.search(r"\b(processes?|tasks?|running)\b", t):
        if not re.search(r"\b(kill|stop|terminate|end)\b", t):
            return [("get_running_processes", {})]

    # ── DISK & SYSTEM ──────────────────────────────────────────────────

    if re.search(r"\b(disk|drive|storage|space|partition)\b", t) and re.search(
            r"\b(usage|space|free|full|how much|size|status)\b", t):
        return [("get_disk_usage", {})]

    if re.search(r"\b(temperature|temp|thermal|hot|heat)\b", t):
        return [("get_temperature", {})]

    # internet check
    if re.search(r"\b(internet|connectivity|online|connected)\b", t) and re.search(
            r"\b(check|is|am i|test|status)\b", t):
        return [("check_internet", {})]

    # ── LOGS & PACKAGES ────────────────────────────────────────────────

    if re.search(r"\b(logs?|journal|syslog|dmesg)\b", t):
        grep = ""
        m = re.search(r"(?:grep|filter|search|find)\s+[\"']?(\w+)", t)
        if m:
            grep = m.group(1)
        return [("view_system_logs", {"log_type": "system", "lines": 30, "grep": grep})]

    if re.search(r"\b(install)\b", t) and re.search(r"\b(package|app|software)\b", t):
        m = re.search(r"(?:install|package)\s+(\S+)", t)
        if m:
            return [("install_package", {"name": m.group(1)})]
    if re.search(r"\b(uninstall|remove|delete)\b", t) and re.search(r"\b(package|app|software)\b", t):
        m = re.search(r"(?:uninstall|remove|delete)\s+(\S+)", t)
        if m:
            return [("uninstall_package", {"name": m.group(1)})]

    # ── NOTIFICATIONS & TTS ────────────────────────────────────────────

    m = re.search(r"\b(?:show|send|display|popup|notify)\b.*?\b(?:toast|notification|alert|message|popup)\b.*?[\"'](.+?)[\"']", t)
    if not m:
        m = re.search(r"\b(?:toast|notification|alert)\b.*?[\"'](.+?)[\"']", t)
    if not m:
        m = re.search(r"(?:show|send|display|notify).*?(?:saying|with|text|message)\s+[\"'](.+?)[\"']", t)
    if not m:
        m = re.search(r"\b(?:show|send|display|popup|notify)\b.*?\b(?:toast|notification|alert|message)\b\s+(.+)", t)
    if m:
        return [("show_toast", {"message": m.group(1).strip()})]

    m = re.search(r"\b(?:speak|say|tell me|read aloud|tts)\b.*?[\"'](.+?)[\"']", t)
    if not m:
        m = re.search(r"(?:speak|say|tell me|read aloud)\s+(.+)", t)
    if m:
        return [("text_to_speech", {"text": m.group(1).strip()})]

    # ── CLIPBOARD ──────────────────────────────────────────────────────

    m = re.search(r"\b(?:copy|clipboard|set clipboard)\b.*?[\"'](.+?)[\"']", t)
    if not m:
        m = re.search(r"\b(?:copy|clipboard|set clipboard)\b\s+(.+)", t)
    if m:
        return [("set_clipboard", {"text": m.group(1).strip()})]

    # ── OPEN APP / SITE ────────────────────────────────────────────────

    m = re.match(r"^(?:open|launch|start)\s+([\w .+-]+?)[.!?]?$", t)
    if m:
        return [("open_app", {"name": m.group(1).strip()})]

    # ── REMOTE TERMINAL ────────────────────────────────────────────────

    # "ls", "ls -la", "ls /home"
    m = re.match(r"^ls\b(.*)$", t)
    if m:
        cmd = "ls" + m.group(1)
        return [("remote_terminal", {"command": cmd})]

    # "run <command>" or "exec <command>" or "execute <command>"
    m = re.match(r"^(?:run|exec|execute|bash|sh|cmd)\s+(.+)$", t)
    if m:
        return [("remote_terminal", {"command": m.group(1).strip()})]

    # "cat /path/to/file"
    m = re.match(r"^cat\s+(.+)$", t)
    if m:
        return [("remote_terminal", {"command": f"cat {m.group(1)}"})]

    # Common shell commands
    if re.match(r"^(?:pwd|whoami|date|uptime|df|df -h|du|du -h|free|free -h|top|htop|ps|ps aux|uname|uname -a|echo .+|mkdir .+|rm .+|cp .+|mv .+|chmod .+|chown .+|which .+|whereis .+|man .+|head .+|tail .+|wc .+|sort .+|grep .+|find .+|locate .+|tar .+|zip .+|unzip .+|curl .+|wget .+|ssh .+|scp .+|rsync .+|git .+|docker .+|podman .+|systemctl .+|journalctl .+|dmesg|lscpu|lsblk|lsusb|lspci|neofetch|screenfetch|cmatrix|sl|cowsay|fortune|figlet)$", t):
        return [("remote_terminal", {"command": t})]

    # "python <args>", "pip <args>", "node <args>", "npm <args>"
    m = re.match(r"^(python|python3|pip|pip3|node|npm|yarn|cargo|go|rustc|gcc|g\+\+|make|cmake|meson|ninja)\s+(.+)$", t)
    if m:
        return [("remote_terminal", {"command": t})]

    # ── OPEN TERMINAL EMULATORS ────────────────────────────────────────

    m = re.match(r"^open\s+(?:the\s+)?(terminal|kitty|alacritty|wezterm|terminology|tilix|konsole|gnome.?terminal|xfce4.?terminal|lxterminal|mate.?terminal|yakuake|dropdown)$", t)
    if m:
        terminal = m.group(1).strip()
        return [("open_app", {"name": terminal})]

    return None
