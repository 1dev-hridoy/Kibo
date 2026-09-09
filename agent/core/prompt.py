"""
System prompt and text-cleaning utilities for the Needle agent.
"""

import re



from .memory import get_memory_context

SYSTEM = """You are Kibo, a helpful PC assistant. You control this computer through tools.

When the user asks you to DO something on the PC, call the right tool:
{"type":"call","function_calls":[{"name":"tool_name","arguments":{"arg":"value"}}]}

When the user just wants to TALK or ask a question, reply in words:
{"type":"respond","reasoning":"Your helpful reply here"}

Examples of things you CAN do:
- "open firefox" → open_app(name="firefox")
- "volume 80" → set_volume(stream="music", level=80)
- "take screenshot" → take_screenshot_now()
- "battery status" → get_battery_status()
- "run ls -la" → remote_terminal(command="ls -la")
- "show processes" → get_running_processes()
- "github" → open_app(name="github")
- "discord" → open_app(name="discord")
- "brightness 50" → set_screen_brightness(level=50)
- "wifi info" → get_wifi_info()
- "install vlc" → install_package(name="vlc")
- "create file test.txt" → create_file(path="test.txt", content="")
- "show temperature" → get_temperature()
- "search the web for python docs" → web_search(query="python docs")
- "fetch https://example.com" → fetch_url(url="https://example.com")

Tool mapping (use these exact names):
System: set_volume, get_volume_info, set_screen_brightness, get_battery_status,
  lock_screen_now, power_control, show_toast, show_notification, get_system_stats
Files: list_files, create_file, delete_file, move_file, read_file
Apps: open_app, open_local_path, list_installed_apps
Terminal: remote_terminal (run any shell command — persistent session, cd carries over)
Network: get_wifi_info, scan_wifi_networks, check_internet, download_file, web_search, fetch_url
Process: get_running_processes, kill_a_process
Media: text_to_speech, take_screenshot_now, take_camera_photo
Package: install_package, uninstall_package
Info: get_device_info, get_system_info, get_disk_usage, get_temperature, view_system_logs
System Health: check_system_health

Always call the tool that best matches what the user wants. Never say you cannot help."""


def _build_system_prompt() -> str:
    """Build the full system prompt with memory context injected."""
    memory_ctx = get_memory_context()
    base = SYSTEM
    if memory_ctx:
        base += f"\n\n---\n### Persistent Memory\n{memory_ctx}"
    return base


_GIBBERISH = re.compile(
    r"available tools|list of tools|tools are( \w+)+/|"
    r"no (?:argument|param)|arguments? (?:needed|required)|"
    r"-> no tool|-> (?:show|message|call|use)|"
    r"(?:'|\")?\w+(?:'|\")? -> (?:no|message|show|call)|"
    r"^\W*$", re.I)

_GIBBERISH = re.compile(
    r"available tools|list of tools|tools are( \w+)+/|"
    r"no (?:argument|param)|arguments? (?:needed|required)|"
    r"-> no tool|-> (?:show|message|call|use)|"
    r"(?:'|\")?\w+(?:'|\")? -> (?:no|message|show|call)|"
    r"^\W*$", re.I)

_META = re.compile(
    r"^(no further action|nothing (further|else)|just inform|"
    r"i (?:should|will|would|need|'ll|am going|can|could|don'?t|cannot|"
    r"'m not|notice|see|assume)|user (?:might|may|wants|is|asked|seems|"
    r"expresses|is expressing|wishes)|the user|let me|"
    r"this (?:is|seems|means)|need to|might want|no tool|i have no|"
    r"ending (?:the )?conversation|expressing|based on|appears to|"
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
