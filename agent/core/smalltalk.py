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


def _tools_list():
    """Return a formatted list of all available tools."""
    lines = ["I have 57 tools:\n"]
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
    lines.append("ADVANCED TOOLS:")
    lines.append("TERMINAL: remote_terminal, remote_terminal_background")
    lines.append("  Execute any shell command remotely")
    lines.append("LAUNCHER: launch_app_smart, get_recent_apps, search_apps")
    lines.append("  Smart app search and launch")
    lines.append("CLIPBOARD SYNC: clipboard_sync_push, pull, list, clear")
    lines.append("  Sync clipboard across devices")
    lines.append("MEDIA: play_media, stop_media, get_media_status, set_media_volume")
    lines.append("  Stream audio/video from URLs")
    lines.append("VOICE: voice_record_start, voice_record_stop, voice_speak, voice_list_devices")
    lines.append("  Voice input/output and recording")
    lines.append("")
    lines.append("MODEL COMMANDS:")
    lines.append("  models / needle / gemma  — Switch AI models")
    lines.append("\nJust tell me what to do naturally!")
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
        return "Running smoothly — all 57 PC tools are ready."
    if re.search(r"who are you|^help", t):
        return ("I'm your local PC agent with 57 tools. I can:\n"
                "- Execute shell commands (remote_terminal)\n"
                "- Launch and search apps (launch_app_smart)\n"
                "- Sync clipboard across devices\n"
                "- Play media from URLs\n"
                "- Record voice and speak text\n"
                "- Control volume, brightness, screenshots\n"
                "- Manage files, processes, and packages\n\n"
                "Try: \"run ls -la\", \"open firefox\", \"play music\"")
    if re.search(r"what (?:tools|can you do|commands|capabilities)|tools? ?list|list tools?|show tools?|available tools?|all tools?|^tools?$", t):
        return _tools_list()
    return ("Hello! Tell me what to do on this PC — try \"run ls -la\", "
            "\"open firefox\", \"play music\", or \"take a screenshot\".")
