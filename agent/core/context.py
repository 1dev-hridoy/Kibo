"""
Context memory for the agent — remembers conversation history
and recent actions for better follow-up handling.
"""

import os
import json
from collections import deque



CONTEXT_DIR = os.path.expanduser("~")
CONTEXT_FILE = os.path.join(CONTEXT_DIR, ".kibo_context.json")
MAX_HISTORY = 10  
MAX_TOOL_HISTORY = 5  




_history = deque(maxlen=MAX_HISTORY)
_tool_history = deque(maxlen=MAX_TOOL_HISTORY)
_user_preferences = {}
_current_task = None


def add_exchange(user_text, agent_text, tool_calls=None, results=None):
    """Add a user-agent exchange to memory."""
    exchange = {
        "user": user_text,
        "agent": agent_text[:200],  


        "tools": [tc.get("name", "") for tc in (tool_calls or [])],
        "timestamp": _get_timestamp(),
    }
    _history.append(exchange)


    if tool_calls:
        for i, tc in enumerate(tool_calls):
            result_str = str(results[i])[:100] if results and i < len(results) else ""
            _tool_history.append({
                "name": tc.get("name", ""),
                "args": tc.get("arguments", {}),
                "result": result_str,
            })

    _detect_current_task(user_text)


def get_context_string():
    """Get recent context as a string for injection into prompts."""
    if not _history:
        return ""

    lines = ["Recent conversation:"]
    for ex in list(_history)[-5:]:  

        
        lines.append(f"User: {ex['user'][:100]}")
        lines.append(f"Agent: {ex['agent'][:100]}")
        if ex["tools"]:
            lines.append(f"Tools used: {', '.join(ex['tools'])}")

    if _current_task:
        lines.append(f"\nCurrent task: {_current_task}")

    if _tool_history:
        recent_tools = [t["name"] for t in list(_tool_history)[-3:]]
        lines.append(f"Recent tools: {', '.join(recent_tools)}")

    return "\n".join(lines)



def get_last_topic():
    """Get the last discussed topic for follow-up handling."""
    if _history:
        last = _history[-1]
        tools = last.get("tools", [])
        if "set_volume" in tools:
            return "volume"
        if "set_screen_brightness" in tools:
            return "brightness"
        if "open_app" in tools:
            return "app"
        if tools:
            return tools[0]
    return None


def get_recent_tools():
    """Get list of recently used tools."""
    return [t["name"] for t in _tool_history]


def get_current_task():
    """Get the current detected task."""
    return _current_task


def set_current_task(task):
    """Manually set the current task."""
    global _current_task
    _current_task = task


def _detect_current_task(text):
    """Detect what the user is trying to do."""
    global _current_task
    text_lower = text.lower()

    if any(w in text_lower for w in ["volume", "sound", "speaker", "mute", "audio"]):
        _current_task = "adjusting volume"
    elif any(w in text_lower for w in ["brightness", "dim", "bright"]):
        _current_task = "adjusting brightness"
    elif any(w in text_lower for w in ["open", "launch", "start"]):
        _current_task = "opening an app"
    elif any(w in text_lower for w in ["screenshot", "capture", "screen"]):
        _current_task = "taking a screenshot"
    elif any(w in text_lower for w in ["install", "uninstall", "package"]):
        _current_task = "managing packages"
    elif any(w in text_lower for w in ["file", "folder", "directory", "create", "delete", "move"]):
        _current_task = "managing files"
    elif any(w in text_lower for w in ["process", "kill", "running"]):
        _current_task = "managing processes"
    elif any(w in text_lower for w in ["wifi", "network", "internet"]):
        _current_task = "checking network"
    elif any(w in text_lower for w in ["battery", "power", "shutdown", "restart"]):
        _current_task = "checking power status"
    elif any(w in text_lower for w in ["play", "music", "video", "media"]):
        _current_task = "playing media"
    elif any(w in text_lower for w in ["copy", "paste", "clipboard"]):
        _current_task = "using clipboard"
    elif any(w in text_lower for w in ["run", "execute", "command", "terminal"]):
        _current_task = "running a command"


def _get_timestamp():
    """Get current timestamp string."""
    from datetime import datetime
    return datetime.now().strftime("%H:%M:%S")


def save_context():
    """Save context to disk."""
    try:
        data = {
            "history": list(_history),
            "tool_history": list(_tool_history),
            "preferences": _user_preferences,
            "current_task": _current_task,
        }
        with open(CONTEXT_FILE, "w") as f:
            json.dump(data, f, indent=2)
    except Exception:
        pass


def load_context():
    """Load context from disk."""
    global _current_task
    try:
        if os.path.exists(CONTEXT_FILE):
            with open(CONTEXT_FILE) as f:
                data = json.load(f)
            _history.extend(data.get("history", []))
            _tool_history.extend(data.get("tool_history", []))
            _user_preferences.update(data.get("preferences", {}))
            _current_task = data.get("current_task")
    except Exception:
        pass


def clear_context():
    """Clear all context."""
    global _current_task
    _history.clear()
    _tool_history.clear()
    _user_preferences.clear()
    _current_task = None
    try:
        if os.path.exists(CONTEXT_FILE):
            os.remove(CONTEXT_FILE)
    except Exception:
        pass



load_context()
