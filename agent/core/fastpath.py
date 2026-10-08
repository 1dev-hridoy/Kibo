"""
Deterministic fast-path routing for PC commands.
Handles 90%+ of user intent without needing the model.
"""

import re
from datetime import datetime
from .typo import correct_typos, find_command_for_app

_last_topic = None


def _num(text, before, after):
    """First 0-100 integer sitting between the two keyword patterns."""
    m = (re.search(before + rf"[^\d%]{{0,24}}(\d{{1,3}})\s*%?", text)
         or re.search(rf"(\d{{1,3}})\s*%?[^\d]{{0,24}}" + after, text))
    return int(m.group(1)) if m and 0 <= int(m.group(1)) <= 100 else None


def _pick_folder(name):
    """Map common folder names to paths."""
    folders = {
        "home": "~", "desktop": "~/Desktop", "documents": "~/Documents",
        "downloads": "~/Downloads", "pictures": "~/Pictures",
        "music": "~/Music", "videos": "~/Videos", "projects": "~/Projects",
        "config": "~/.config", "documents": "~/Documents",
    }
    return folders.get(name.lower(), f"~/{name}")


def _fastpath(text):
    """Route user input to tool calls. Returns list of (tool, args) or None."""
    global _last_topic

    t = correct_typos(text.lower().strip())
    # Remove trailing punctuation
    t = re.sub(r"[.!?]+$", "", t).strip()

    # ═══════════════════════════════════════════════════════════════════
    # MODEL MANAGEMENT
    # ═══════════════════════════════════════════════════════════════════
    m = re.match(r"^(?:switch|change|use)\s+(?:to\s+)?(?:the\s+)?(?:model\s+)?(\w+)$", t)
    if m:
        if m.group(1).lower() in ("model", "models"):
            return "__models__", None
        return "__switch_model__", m.group(1).lower()
    if t in ("needle", "needle2", "n", "gemma", "google", "func", "functiongemma", "fg"):
        return "__switch_model__", t
    if re.match(r"^(?:what|which|current|active)\s+model$", t):
        return "__current_model__", None
    if re.match(r"^(?:list|show)\s+models?$", t):
        return "__models__", None

    _pet_any = ("fireworks", "firework", "boom", "cracker", "blast",
                "sparkle", "sparkles", "shiny", "twinkle", "glitter",
                "orbit", "satellite", "halo", "rainbow", "pride", "colors",
                "music", "sing", "song", "melody", "tune", "humming",
                "giggle", "teehee", "laugh", "dance", "celebrate", "party",
                "yay", "hooray", "clap", "zoomies", "zoom",
                "heartrain", "heart rain", "hearts rain", "falling hearts",
                "shower", "love", "hearts", "heart", "hug", "kiss", "cuddle",
                "sleepy", "yawn", "nap", "bedtime", "go to sleep",
                "mochi", "pixel", "showcase", "parade", "play all", "show all")


    
    _pet_distinct = ("fireworks", "firework", "boom", "cracker", "blast",
                     "sparkle", "sparkles", "shiny", "twinkle", "glitter",
                     "orbit", "satellite", "halo", "rainbow", "pride",
                     "music", "sing", "song", "melody", "tune",
                     "giggle", "teehee", "laugh", "dance", "celebrate",
                     "party", "yay", "hooray", "zoomies", "zoom",
                     "heartrain", "heart rain", "shower", "love", "hearts",
                     "hug", "kiss", "cuddle", "sleepy", "yawn", "nap",
                     "bedtime", "go to sleep", "mochi", "pixel", "showcase", "parade", "play all", "show all")
    if re.search(r"\b(pet|kibo|mochi)\b", t) and any(w in t for w in _pet_any):
        return [("pet_animate", {"action": t})]

    if re.search(r"\bi love you\b", t):
        return [("pet_love", {})]
    if len(t.split()) <= 3 and not re.search(r"\d", t) and \
            any(w in t for w in _pet_distinct):
        return [("pet_animate", {"action": t})]


    m = re.match(r"^pet\s+show\s+(.+)$", t)
    if m:
        return [("pet_show", {"text": m.group(1).strip()})]
    m = re.match(r"^pet\s+send\s+(.+)$", t)
    if m:
        return [("pet_send", {"text": m.group(1).strip()})]
    m = re.match(r"^(?:kibo\s+message\s+set|set\s+(?:kibo\s+|widget\s+)?message|set\s+(?:kibo|widget)|widget\s+(?:show|set)|show\s+(?:on\s+)?(?:the\s+)?widget)\s+(.+)$", t)
    if m and not re.search(r"\b(volume|brightness|sound|model)\b", m.group(1)):
        return [("widget_set_message", {"message": m.group(1).strip()})]
    if re.match(r"^(?:clear|reset|hide)\s+(?:the\s+)?widget(?:\s+message|\s+text)?$|^(?:widget|pet|weight|wedget|wiget)\s+(?:clear|reset|hide|free)$", t):
        return [("widget_clear", {})]
    if re.search(r"\bwidget\b.*\bfree\b|\bfree\b.*\bwidget\b", t):
        return [("widget_clear", {})]
    if re.search(r"\bdrink\b.*\bwater\b|\bwater\b.*\bdrink\b|\bhydrate\b|\bglass of water\b", t):
        return [("remind_water", {})]
    if re.search(r"\btouch grass\b|\bgo outside\b|\bfresh air\b", t):
        return [("remind_grass", {})]
    if re.match(r"^(?:time to |go |come on,? )?(?:stretch|do some stretching)(?:\s+(?:a bit|now|please))?$", t):
        return [("remind_stretch", {})]
    if re.search(r"\b(?:rest|give).*eyes\b|\beye break\b|\bblink\b.*\bbreak\b|\b20-20-20\b", t):
        return [("remind_eyes", {})]
    if re.search(r"\bposture\b|\bsit (?:up )?straight\b|\bstraighten.*back\b|\bsit tall\b", t):
        return [("remind_posture", {})]
    if re.match(r"^(?:turn\s+)?reminders?\s+on$|^(?:enable|start)\s+reminders?$", t):
        return [("reminders_on", {})]
    if re.match(r"^(?:turn\s+)?reminders?\s+off$|^(?:disable|stop|pause)\s+reminders?$", t):
        return [("reminders_off", {})]
    if re.match(r"^reminders?(?:\s+status)?$", t):
        return [("reminders_status", {})]
    if re.match(r"^(?:(?:brief|breaf|breif|brif)(?:\s+(?:me|today|the\s+day))?|daily\s+brief(?:ing)?|morning\s+brief(?:ing)?|today'?s\s+brief(?:ing)?|what'?s\s+(?:up|on)\s+today)$", t):
        return [("brief_today", {})]
    if re.match(r"^(?:turn\s+)?briefing\s+on$|^(?:enable|start)\s+(?:daily\s+)?briefing$", t):
        return [("briefing_on", {})]
    if re.match(r"^(?:turn\s+)?briefing\s+off$|^(?:disable|stop)\s+(?:daily\s+)?briefing$", t):
        return [("briefing_off", {})]
    if re.match(r"^briefing(?:\s+status)?$", t):
        return [("briefing_status", {})]
    if re.match(r"^(?:live(?:\s+(?:screen|view))?|show\s+(?:live|my)\s+screen)$", t):
        return [("take_screenshot_now", {})]

    # ═══════════════════════════════════════════════════════════════════
    # VOLUME
    # ═══════════════════════════════════════════════════════════════════
    if re.search(r"\bmute\b", t) and "unmute" not in t:
        _last_topic = "volume"
        return [("set_volume", {"stream": "music", "level": 0})]
    if re.search(r"\bunmute\b", t):
        _last_topic = "volume"
        return [("set_volume", {"stream": "music", "level": 60})]
    if re.search(r"\b(volume|sound|speaker|audio)\b", t):
        n = _num(t, r"\b(?:volume|sound|speaker|audio)\b", r"")
        if n is None and re.search(r"\b(max|full|highest|loudest)\b", t):
            n = 100
        if n is None and re.search(r"\b(min|lowest|quietest)\b", t):
            n = 0
        if n is None and re.search(r"\b(up|louder|increase|higher|more)\b", t):
            n = 90
        if n is None and re.search(r"\b(down|quieter|decrease|lower|less)\b", t):
            n = 30
        if n is not None:
            _last_topic = "volume"
            return [("set_volume", {"stream": "music", "level": n})]
        if re.search(r"\b(what|how|current|get|show|check|level)\b", t):
            return [("get_volume_info", {})]

    # Follow-up: "make it 50" / "set it to 50"
    if _last_topic == "volume":
        m = re.match(r"^(?:make|set|turn|change)\s+(?:it|that)?\s*(?:to)?\s*(\d{1,3})\s*%?$", t)
        if m and 0 <= int(m.group(1)) <= 100:
            return [("set_volume", {"stream": "music", "level": int(m.group(1))})]

    # ═══════════════════════════════════════════════════════════════════
    # BRIGHTNESS
    # ═══════════════════════════════════════════════════════════════════
    if re.search(r"\b(brightness|brighter|dim|dimmer|screen light)\b", t):
        n = _num(t, r"\b(?:brightness|brighter|dimmer?|screen)\b", r"")
        if n is None and re.search(r"\b(max|full|highest|brightest)\b", t):
            n = 100
        if n is None and re.search(r"\b(min|lowest|dimmest|dark)\b", t):
            n = 10
        if n is None and re.search(r"\b(up|brighter|increase|higher|more)\b", t):
            n = 90
        if n is None and re.search(r"\b(down|dimmer|decrease|lower|less)\b", t):
            n = 30
        if n is not None:
            _last_topic = "brightness"
            return [("set_screen_brightness", {"level": n})]

    if _last_topic == "brightness":
        m = re.match(r"^(?:make|set|turn|change)\s+(?:it|that)?\s*(?:to)?\s*(\d{1,3})\s*%?$", t)
        if m and 0 <= int(m.group(1)) <= 100:
            return [("set_screen_brightness", {"level": int(m.group(1))})]

    # ═══════════════════════════════════════════════════════════════════
    # SCREENSHOT
    # ═══════════════════════════════════════════════════════════════════
    if re.search(r"\b(screenshot|screen ?shot|capture|snip)\b", t):
        return [("take_screenshot_now", {})]
    if re.match(r"^(?:take|grab|get|capture)\s+(?:a\s+)?(?:screen|screenshot|pic|photo)$", t):
        return [("take_screenshot_now", {})]

    # ═══════════════════════════════════════════════════════════════════
    # LOCK / SHUTDOWN / RESTART / SLEEP
    # ═══════════════════════════════════════════════════════════════════
    if re.search(r"\block\b", t):
        return [("lock_screen_now", {})]
    if re.search(r"\b(shut ?down|power ?off|turn off)\b", t):
        return [("power_control", {"action": "shutdown"})]
    if re.search(r"\b(restart|reboot)\b", t):
        return [("power_control", {"action": "restart"})]
    if re.search(r"\b(sleep|suspend|hibernate)\b", t):
        return [("power_control", {"action": "sleep"})]

    # ═══════════════════════════════════════════════════════════════════
    # BATTERY
    # ═══════════════════════════════════════════════════════════════════
    if re.search(r"\b(battery|charge|charging)\b", t):
        return [("get_battery_status", {})]

    # ═══════════════════════════════════════════════════════════════════
    # SYSTEM INFO
    # ═══════════════════════════════════════════════════════════════════
    if re.search(r"\b(cpu|ram|memory)\b", t):
        return [("get_system_stats", {})]
    if re.search(r"\b(device|system|pc|computer|machine|specs?|info)\b", t):
        return [("get_device_info", {})]
    if re.search(r"\b(temperature|temp|thermal|hot|heat)\b", t):
        return [("get_temperature", {})]
    if re.search(r"\b(disk|drive|storage|space)\b", t):
        return [("get_disk_usage", {})]
    if re.search(r"\b(internet|online|connect|wifi|network)\b", t) and \
       re.search(r"\b(check|is|am i|status|working)\b", t):
        return [("check_internet", {})]

    # ═══════════════════════════════════════════════════════════════════
    # WIFI
    # ═══════════════════════════════════════════════════════════════════
    if re.search(r"\b(wi-?fi|network|ssid)\b", t):
        if re.search(r"\b(scan|nearby|around|available|list|see)\b", t):
            return [("scan_wifi_networks", {})]
        return [("get_wifi_info", {})]

    # ═══════════════════════════════════════════════════════════════════
    # TIME / DATE
    # ═══════════════════════════════════════════════════════════════════
    if re.search(r"\b(time|clock|hour)\b", t) and \
       re.search(r"\b(what|whats|tell|current|now|is it)\b", t):
        now = datetime.now().strftime("%I:%M %p")
        return "__reply__", f"The current time is {now}."
    if re.search(r"\b(date|day|today)\b", t) and \
       re.search(r"\b(what|whats|tell|current|now|is it)\b", t):
        now = datetime.now().strftime("%A, %B %d, %Y")
        return "__reply__", f"Today is {now}."

    # ═══════════════════════════════════════════════════════════════════
    # PROCESSES
    # ═══════════════════════════════════════════════════════════════════
    m = re.match(r"^(?:kill|stop|terminate|end)\s+(?:the\s+)?(?:process|pid|task)?\s*(\d+)$", t)
    if m:
        return [("kill_a_process", {"pid": int(m.group(1))})]
    if re.search(r"\b(processes?|tasks?|running|what'?s running)\b", t):
        return [("get_running_processes", {})]

    # ═══════════════════════════════════════════════════════════════════
    # APP CONTROL (focus, minimize, maximize, close, type, hotkey)
    # ═══════════════════════════════════════════════════════════════════
    m = re.match(r"^(?:focus|bring|activate|switch to)\s+(?:the\s+)?(.+)$", t)
    if m:
        return [("focus_app", {"name": m.group(1).strip()})]
    m = re.match(r"^(?:minimize|min)\s+(?:the\s+)?(.+)$", t)
    if m:
        return [("minimize_app", {"name": m.group(1).strip()})]
    m = re.match(r"^(?:maximize|max|fullscreen)\s+(?:the\s+)?(.+)$", t)
    if m:
        return [("maximize_app", {"name": m.group(1).strip()})]
    m = re.match(r"^(?:close|quit|exit|kill)\s+(?:the\s+)?(.+)$", t)
    if m:
        return [("close_app", {"name": m.group(1).strip()})]
    m = re.match(r"^(?:type|write|input)\s+(?:in|into|on)\s+(.+?)\s*:\s*(.+)$", t)
    if m:
        return [("type_in_app", {"name": m.group(1).strip(), "text": m.group(2).strip()})]
    m = re.match(r"^(?:hotkey|shortcut|press)\s+(?:in|on)\s+(.+?)\s*:\s*(.+)$", t)
    if m:
        return [("hotkey_in_app", {"name": m.group(1).strip(), "keys": m.group(2).strip()})]
    if re.match(r"^(?:list|show)\s+(?:open\s+)?windows?$", t):
        return [("list_windows", {})]
    if re.match(r"^(?:what|which)\s+(?:window|app)\s+(?:is\s+)?(?:active|focused|open)$", t):
        return [("get_active_window", {})]

    # ═══════════════════════════════════════════════════════════════════
    # FILE OPERATIONS
    # ═══════════════════════════════════════════════════════════════════

    m = re.match(r"^(?:open|show|view|list|browse|see)\s+(?:my\s+)?(?:the\s+)?(downloads?|documents?|desktop|pictures?|music|videos?|projects?|home|config)$", t)
    if m:
        return [("list_files", {"path": _pick_folder(m.group(1))})]

    m = re.match(r"^(?:what'?s|what is|what are)\s+in\s+(?:my\s+)?(?:the\s+)?(\w+)$", t)
    if m:
        return [("list_files", {"path": _pick_folder(m.group(1))})]
   
    m = re.search(r"\b(list|show|browse)\s+(?:files?|contents?)\s+(?:in|at|from)\s+[\"']?([/~\w.\- ]+)[\"']?", t)
    if m:
        return [("list_files", {"path": m.group(1).strip()})]
    # "read file /path"
    m = re.search(r"\b(read|open|cat|view|show)\s+(?:the\s+)?file\s+[\"']?([/~\w.\- ]+)", t)
    if m:
        return [("read_file", {"path": m.group(1).strip()})]
    # "installed apps" / "what apps"
    if re.search(r"\b(list|show|what|which)\b", t) and \
       re.search(r"\b(installed|apps?|software|packages?|programs?)\b", t):
        return [("list_installed_apps", {})]
    # "logs" / "system logs"
    if re.search(r"\b(logs?|journal|syslog|dmesg)\b", t):
        return [("view_system_logs", {"log_type": "system", "lines": 30, "grep": ""})]

    # ═══════════════════════════════════════════════════════════════════
    # NOTIFICATIONS / TTS / CLIPBOARD
    # ═══════════════════════════════════════════════════════════════════
    if re.match(r"^(?:(?:list|show|what are|give me)(?:\s+(?:me|all|the|my))*\s+(?:pet\s+)?animations?(?:\s+list)?|animations?(?:\s+list)?)$", t):
        previews = [
            ("sparkle", "say 'sparkle please'"),
            ("fireworks", "say 'fireworks please'"),
            ("orbit", "say 'orbit stars'"),
            ("heart rain", "say 'rain hearts'"),
            ("music", "say 'sing a song'"),
            ("rainbow", "say 'show a rainbow'"),
            ("giggle", "say 'giggle please'"),
            ("zoomies", "say 'zoom around'"),
            ("dance", "say 'dance with kibo'"),
            ("love", "say 'send love'"),
            ("happy", "say 'be happy'"),
            ("sleepy", "say 'go to sleep'"),
            ("pixel cat", "say 'pixel cat'"),
            ("everything, one by one", "say 'showcase'"),
        ]
        lines = ["Pet animations — try one:"] + [f"  - {name}: {how}" for name, how in previews]
        return "__reply__", "\n".join(lines)

    m = re.search(r"(?:show|send|display|notify|toast).*?[\"'](.+?)[\"']", t)
    if not m:
        m = re.search(r"(?:show|send|display|notify|toast)\s+(.+)", t)
    if m and len(m.group(1)) > 1:
        return [("show_toast", {"message": m.group(1).strip()})]

    m = re.search(r"(?:speak|say|tell me|read aloud|tts)\s+[\"'](.+?)[\"']", t)
    if not m:
        m = re.search(r"(?:speak|say|tell me|read aloud)\s+(.+)", t)
    if m:
        return [("text_to_speech", {"text": m.group(1).strip()})]

    m = re.search(r"(?:copy|clipboard)\s+[\"'](.+?)[\"']", t)
    if not m:
        m = re.search(r"(?:copy|clipboard)\s+(.+)", t)
    if m:
        return [("set_clipboard", {"text": m.group(1).strip()})]
    if re.search(r"\b(paste|clipboard)\b", t) and re.search(r"\b(get|read|show|what)\b", t):
        return [("get_clipboard", {})]

    # ═══════════════════════════════════════════════════════════════════
    # LIVE SCREEN
    # ═══════════════════════════════════════════════════════════════════
    if re.match(r"^(?:live|watch|view|show)\s*(?:screen|display|monitor)$", t):
        return [("take_screenshot_now", {})]

    # ═══════════════════════════════════════════════════════════════════
    # ALERTS
    # ═══════════════════════════════════════════════════════════════════
    m = re.match(r"^(?:alert|notify|warn)\s+(?:me\s+)?(?:when|if)\s+(.+?)\s+(?:goes?\s+)?(?:above|over|higher)\s+(\d+)$", t)
    if m:
        return [("add_alert", {"metric": m.group(1), "threshold": int(m.group(2)), "direction": "above"})]
    m = re.match(r"^(?:alert|notify|warn)\s+(?:me\s+)?(?:when|if)\s+(.+?)\s+(?:goes?\s+)?(?:below|under|lower)\s+(\d+)$", t)
    if m:
        return [("add_alert", {"metric": m.group(1), "threshold": int(m.group(2)), "direction": "below"})]
    if re.match(r"^(?:list|show|check)\s+(?:my\s+)?alerts?$", t):
        return [("get_alert_summary", {})]

    # ═══════════════════════════════════════════════════════════════════
    # SCHEDULING
    # ═══════════════════════════════════════════════════════════════════
    m = re.match(r"^(?:schedule|remind(?:\s+me)?\s+to)\s+(.+?)(?:\s+(?:in|after|every)\s+(\d+)\s*(s|sec|m|min|h|hr|hour)s?)?$", t)
    if m:
        cmd = m.group(1).strip()
        delay = 0
        repeat = 0
        if m.group(2):
            num = int(m.group(2))
            unit = m.group(3)
            if unit.startswith("h"):
                delay = num * 3600
            elif unit.startswith("m"):
                delay = num * 60
            else:
                delay = num
            if "every" in t:
                repeat = delay
                delay = 0
        return [("schedule_agent_task", {"instruction": cmd, "delay": delay, "repeat": repeat})]
    if re.match(r"^(?:list|show)\s+(?:my\s+)?(?:tasks?|jobs?|schedule)$", t):
        return [("list_tasks", {})]

    # ═══════════════════════════════════════════════════════════════════
    # OPEN APP / WEBSITE
    # ═══════════════════════════════════════════════════════════════════
    m = re.match(r"^(?:open|launch|start|run|boot)\s+(.+)$", t)
    if m:
        app_name = m.group(1).strip()
        cmd, source = find_command_for_app(app_name)
        if cmd:
            if source == "url_map":
                return [("open_app", {"name": app_name})]
            elif source in ("which", "process"):
                return [("remote_terminal", {"command": cmd[0]})]
        return [("open_app", {"name": app_name})]

    # Single word → try to open as app/site (e.g. "github", "firefox", "chrome")
    m = re.match(r"^([\w.-]+)$", t)
    if m and len(m.group(1)) > 2:
        word = m.group(1).strip()
        cmd, source = find_command_for_app(word)
        if cmd:
            if source == "url_map":
                return [("open_app", {"name": word})]
            elif source in ("which", "process"):
                return [("remote_terminal", {"command": cmd[0]})]
            else:
                return [("open_app", {"name": word})]

    # ═══════════════════════════════════════════════════════════════════
    # SHELL COMMANDS
    # ═══════════════════════════════════════════════════════════════════
    # "run <command>" / "exec <command>" / "execute <command>"
    m = re.match(r"^(?:run|exec|execute|bash|sh|cmd)\s+(.+)$", t)
    if m:
        return [("remote_terminal", {"command": m.group(1).strip()})]
    # Common shell commands
    if re.match(r"^(ls|pwd|whoami|date|uptime|df|du|free|top|htop|ps|uname|neofetch|"
                r"cat|head|tail|wc|sort|grep|find|mkdir|rm|cp|mv|chmod|chown|which|"
                r"tar|zip|unzip|curl|wget|ssh|git|docker|systemctl|journalctl)\b", t):
        return [("remote_terminal", {"command": t})]
    # Programming tools
    if re.match(r"^(python|python3|pip|node|npm|yarn|cargo|gcc|make|cmake)\s+", t):
        return [("remote_terminal", {"command": t})]

    # ═══════════════════════════════════════════════════════════════════
    # MULTI-PC
    # ═══════════════════════════════════════════════════════════════════
    m = re.match(r"^(?:switch|go)\s+to\s+(?:pc|computer|machine)?\s*(.+)$", t)
    if m:
        return [("switch_to_pc", {"name": m.group(1).strip()})]
    m = re.match(r"^(?:register|add)\s+(?:pc|computer|machine)\s+(\S+)\s+(\S+)$", t)
    if m:
        return [("register_remote_pc", {"name": m.group(1), "host": m.group(2)})]
    if re.match(r"^(?:list|show)\s+(?:my\s+)?(?:pcs?|computers?|machines?)$", t):
        return [("list_remote_pcs", {})]
    m = re.match(r"^(?:ping|check)\s+(.+)$", t)
    if m:
        return [("ping_remote_pc", {"name": m.group(1).strip()})]

    # ═══════════════════════════════════════════════════════════════════
    # MACROS
    # ═══════════════════════════════════════════════════════════════════
    m = re.match(r"^(?:record|start recording)\s+(?:macro\s+)?(.+)$", t)
    if m:
        return [("start_macro_recording", {"name": m.group(1).strip()})]
    if re.match(r"^(?:stop|end)\s+(?:recording|macro)$", t):
        return [("stop_macro_recording", {})]
    m = re.match(r"^(?:replay|play|run)\s+(?:macro\s+)?(.+)$", t)
    if m:
        return [("replay_macro", {"name": m.group(1).strip()})]
    if re.match(r"^(?:list|show)\s+(?:my\s+)?macros?$", t):
        return [("list_macros", {})]

    # ═══════════════════════════════════════════════════════════════════
    # GREETINGS / HELP
    # ═══════════════════════════════════════════════════════════════════
    if re.match(r"^(?:hello|hi|hey|howdy|sup|yo|greetings|good\s*(?:morning|afternoon|evening))$", t):
        return "__reply__", "Hey! I'm Kibo — your PC assistant. Tell me what to do."
    if re.match(r"^(?:help|what can you do|capabilities|commands|features)$", t):
        tools = [
            "volume/brightness control", "screenshot", "lock/shutdown/restart",
            "open apps & websites", "file management", "process management",
            "WiFi info", "battery status", "system stats", "notifications",
            "text-to-speech", "clipboard", "shell commands", "multi-PC control",
            "macro recording", "scheduled tasks", "alerts",
        ]
        return "__reply__", "I can help with:\n" + "\n".join(f"  - {t}" for t in tools)

    # ═══════════════════════════════════════════════════════════════════
    # FALLBACK — let the model try
    # ═══════════════════════════════════════════════════════════════════
    return None
