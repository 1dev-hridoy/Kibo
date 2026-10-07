"""
Small talk and greetings handling for the agent.
"""

import re

_GREETING = re.compile(
    r"^(?:hi+|hello+|hey+|yo|hiya|howdy|(?:hi+|hello+|hey+) there|"
    r"good (?:morning|afternoon|evening)|"
    r"(?:thanks|thank you|thx|ty)(?:[!,. ]*(?:a lot|so much|good (?:bot|job|work)|nice))?|"
    r"how are you|how(?:'?s| is) it going|what(?:'?s| is) up|sup|"
    r"who are you|what can you do|help(?:[ ]me)?|"
    r"what tools|tools? ?list|list tools?|show tools?|available tools?|all tools?|"
    r"^tools?$|"
    r"what (?:commands?|capabilities|features)|"
    r"good (?:bot|job|work)|nice)[!,.? ]*$", re.I)


def _tools_count():
    from agent.tools import ALL_TOOLS
    return len(ALL_TOOLS)


def _tools_list():
    """Return a formatted list of real tool names grouped by module."""
    from agent.tools import ALL_TOOLS
    lines = [f"I have {len(ALL_TOOLS)} tools. Some of them:\n"]
    lines.append("SYSTEM: show_toast, show_notification, get_battery_status,")
    lines.append("  set_clipboard, get_clipboard, set_screen_brightness,")
    lines.append("  get_volume_info, set_volume, lock_the_screen, get_system_stats")
    lines.append("HARDWARE: get_device_info, take_screenshot_now, lock_screen_now, power_control")
    lines.append("CLIPBOARD: copy_text_to_clipboard, read_clipboard_text")
    lines.append("MEDIA: take_camera_photo, text_to_speech, record_audio_start, record_audio_stop")
    lines.append("NETWORK: get_wifi_info, scan_wifi_networks, check_internet,")
    lines.append("  download_file, get_system_info")
    lines.append("APPS: open_app, open_local_path, list_files, list_installed_apps")
    lines.append("PROCESS: get_running_processes, kill_a_process")
    lines.append("FILES: create_file, delete_file, move_file, read_file")
    lines.append("DISK: get_disk_usage, get_temperature")
    lines.append("LOGS: view_system_logs")
    lines.append("PACKAGES: install_package, uninstall_package")
    lines.append("")
    names = [t.__name__ for t in ALL_TOOLS]
    lines.append("RECENT: " + ", ".join(names[:12]) + " ...")
    lines.append("\nType 'models' to switch models, 'tools' for more.")
    return "\n".join(lines)


def _smalltalk(text):
    """Direct answers for greetings — keeps the tiny model from
    hallucinating tool calls on small talk."""
    t = text.lower().strip()
    if not _GREETING.match(t):
        return None
    if re.search(r"thank|thx|\bty\b|good (bot|job|work)|nice", t):
        return "You're welcome! Anything else on this PC?"
    if re.search(r"how are you|how('?s| is) it going|what('?s| is) up|sup", t):
        import random
        return random.choice([
            f"Running smoothly — all {_tools_count()} PC tools are ready.",
            f"Doing great! {_tools_count()} tools standing by.",
            f"Always ready with {_tools_count()} tools at your command.",
        ])
    if re.search(r"who are you|^help", t):
        import random
        n = _tools_count()
        return random.choice([
            f"I'm Kibo, your local PC agent with {n} tools on this machine. I can run shell commands, open apps, manage files, control volume/brightness, take screenshots, do network and security scans, and more. Try: \"run ls -la\", \"open firefox\", \"take a screenshot\".",
            f"I'm Kibo — a private, on-device assistant with {n} tools. I can do system control, file management, web search, voice, macros, and Linux security checks. Just tell me naturally, e.g. \"check battery\" or \"lock screen\".",
            f"I'm Kibo, your chat-controlled PC agent — {n} tools ready: from \"set volume to 80\" to \"describe my wifi\". Everything stays local; no cloud needed.",
        ])
    if re.search(r"what (?:tools|can you do|commands|capabilities)|tools? ?list|list tools?|show tools?|available tools?|all tools?|^tools?$", t):
        return _tools_list()
    return ("Hello! Tell me what to do on this PC — try \"run ls -la\", "
            "\"open firefox\", \"play music\", or \"take a screenshot\".")
