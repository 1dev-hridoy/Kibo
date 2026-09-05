"""
System prompt and text-cleaning utilities for the Needle agent.
"""

import re

SYSTEM = """You control this PC through tools. Reply with exactly one JSON envelope.

To answer in words:
{"type":"respond","reasoning":"<your reply to the user>"}
The reasoning field IS the message shown to the user. Write it as plain, friendly prose that answers the user directly. Never write notes to yourself or mention tools in it.

To act, call a tool:
{"type":"call","function_calls":[{"name":"...","arguments":{...}}]}

After tool results arrive, reply with a respond envelope that states the outcome in words (e.g. "The volume is now at 100%.").
...
Mappings: set volume/sound/speaker level -> set_volume with level 0-100; ask current volume -> get_volume_info; brightness percent -> set_screen_brightness; battery -> get_battery_status; cpu or ram/memory usage -> get_system_stats; wifi or network connection details -> get_wifi_info; nearby wifi networks -> scan_wifi_networks; internet connectivity -> check_internet; screenshot of the screen -> take_screenshot_now; lock the screen -> lock_screen_now or lock_the_screen; shut down / restart / sleep the PC -> power_control; popup message -> show_toast; notification -> show_notification; copy text -> set_clipboard; read clipboard -> get_clipboard; speak text aloud -> text_to_speech; webcam photo -> take_camera_photo; open an app or website -> open_app; open a local file or folder -> open_local_path; list files in a folder -> list_files; show installed apps -> list_installed_apps; running processes -> get_running_processes; kill a process by PID -> kill_a_process; create a file -> create_file; delete a file -> delete_file; move/rename a file -> move_file; read file contents -> read_file; disk space usage -> get_disk_usage; system temperature -> get_temperature; view logs -> view_system_logs; install software -> install_package; uninstall software -> uninstall_package; PC model/OS/hostname -> get_device_info; OS/hostname/architecture info -> get_system_info; download a URL -> download_file. Whenever the user asks about or wants to change something on this PC, use the matching tool. Use respond only for greetings, thanks, and general chat."""

_GIBBERISH = re.compile(
    r"available tools|list of tools|tools are( \w+)+/|"
    r"no (?:argument|param)|arguments? (?:needed|required)|"
    r"-> no tool|-> (?:show|message|call|use)|"
    r"(?:'|\")?\w+(?:'|\")? -> (?:no|message|show|call)|"
    r"^\W*$", re.I)

_META = re.compile(
    r"^(no further action|nothing (further|else)|just inform|"
    r"i (should|will|would|need|'ll|am going|can|could|don'?t|cannot|"
    r"'m not|notice|see|assume)|user (might|may|wants|is|asked|seems|"
    r"expresses|is expressing|wishes)|the user|let me|"
    r"this (is|seems|means)|need to|might want|no tool|i have no|"
    r"ending (the )?conversation|expressing|based on|appears to|"
    r"seems to|looks like|the request|the query|the command|"
    r"no stream specified|implies|->|"
    r"(?:\w+) -> (?:no tool|not a tool|"
    r"(?:'|\")?\w+(?:'|\")? -> (?:show|no|message)|"
    r"use \w+|call \w+|try \w+)|"
    r"(?:'|\")?\w+(?:'|\")? is (?:a |the )?(?:tool|command|function)|"
    r"no (?:argument|param)|arguments? (?:needed|required)|"
    r"(?:the )?(?:user )?(?:wants?|is asking|said|means?)|"
    r"(?:i |we )?(?:should|will|can|could|would|might) "
    r"(?:use|call|try|send|return|reply|answer|provide|"
    r"show|display|execute|run|invoke)|"
    r"(?:no|not) (?:need|require|use) "
    r"(?:for|to|with) (?:this|that|the)|"
    r"(?:that|this) (?:is|means|requires|needs|implies))", re.I)


def _strip_meta(text):
    """Drop self-talk sentences the engine leaks into reasoning."""
    text = (text or "").strip()
    if not text:
        return text
    keep = [s for s in re.split(r"(?<=[.!?])\s+", text)
            if not _META.match(s.strip())]
    cleaned = " ".join(keep) if keep else text
    return "" if _GIBBERISH.search(cleaned) else cleaned


def _fallback():
    return ("I couldn't work out how to do that. Try commands like: "
            "\"set volume to 80\", \"battery status\", \"wifi info\", "
            "\"take a screenshot\", or just ask me anything.")
