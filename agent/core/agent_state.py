"""
Agent state — shared between web app and engine without circular imports.
Tracks overall state plus which tool is currently executing.
"""

import time as _time

_agent_state = {
    "state": "idle",           
    "current_task": "",
    "current_tool": "",       
    "tools_done": 0,          
    "tools_total": 0,         
    "history": [],             
    "custom_message": "",      
    "custom_animation": "fade",
    "custom_expires_in": 0,
    "pet_action": "",
    "pet_seq": 0,
    "_idle_since": 0.0,        
}


def get_agent_state():
    return _agent_state


HISTORY_LIMIT = 30


def read_history():
    """Every widget message ever set, oldest first."""
    try:
        import json as _json
        import os as _os
        path = _os.path.expanduser("~/.config/kibo/pet_history.json")
        with open(path) as f:
            items = _json.load(f)
        if not isinstance(items, list):
            return []
        return [str(i) for i in items if str(i).strip()]
    except (OSError, ValueError, AttributeError):
        return []


def _append_history(message):
    try:
        import json as _json
        import os as _os
        path = _os.path.expanduser("~/.config/kibo/pet_history.json")
        _os.makedirs(_os.path.dirname(path), exist_ok=True)
        items = read_history()
        items.append(message[:80])
        del items[:-HISTORY_LIMIT]
        tmp = path + ".tmp"
        with open(tmp, "w") as f:
            _json.dump(items, f)
        _os.replace(tmp, path)
    except OSError:
        pass


def write_pet_message(message: str, animation: str = "fade",
                        expires_in: int = 0):
    """Set the current widget message without adding to the history."""
    _agent_state["custom_message"] = message[:80]
    _agent_state["custom_animation"] = animation or "fade"
    _agent_state["custom_expires_in"] = expires_in
    try:
        import json as _json
        import os as _os
        path = _os.path.expanduser("~/.config/kibo/pet_message.json")
        _os.makedirs(_os.path.dirname(path), exist_ok=True)
        tmp = path + ".tmp"
        with open(tmp, "w") as f:
            _json.dump({"message": message[:80],
                        "animation": animation or "fade",
                        "expires_in": expires_in}, f)
        _os.replace(tmp, path)
    except OSError:
        pass


def set_widget_message(message: str, animation: str = "fade",
                         expires_in: int = 0):
    """Set a custom message shown in the desktop widget.

    expires_in=0 means the message persists until explicitly cleared.
    Transient notifications (reminders) pass a small positive value.
    Every message is also recorded in the history file.
    """
    write_pet_message(message, animation, expires_in)
    _append_history(message)


def read_pet_message_file():
    try:
        import json as _json
        import os as _os
        path = _os.path.expanduser("~/.config/kibo/pet_message.json")
        with open(path) as f:
            data = _json.load(f)
        return (data.get("message", ""), data.get("animation", "fade"),
                int(data.get("expires_in", 0) or 0))
    except (OSError, ValueError, AttributeError):
        return "", "fade", 0


def clear_widget_message():
    _agent_state["custom_message"] = ""
    _agent_state["custom_animation"] = "fade"
    _agent_state["custom_expires_in"] = 0
    try:
        import os as _os
        path = _os.path.expanduser("~/.config/kibo/pet_message.json")
        if _os.path.exists(path):
            _os.remove(path)
    except OSError:
        pass


def update_agent_state(state: str, task: str = ""):
    _agent_state["state"] = state
    _agent_state["current_task"] = task
    if state == "idle":
        _agent_state["current_tool"] = ""
        _agent_state["tools_done"] = 0
        _agent_state["tools_total"] = 0
        _agent_state["_idle_since"] = _time.time()

   


def is_recently_active(cooldown: float = 3.0) -> bool:
    """True if we were active within the last `cooldown` seconds."""
    if _agent_state["state"] != "idle":
        return True
    return (_time.time() - _agent_state.get("_idle_since", 0)) < cooldown


def begin_task(task: str, total_tools: int = 0):
    """Called when the agent starts processing a new request."""
    update_agent_state("working", task)
    _agent_state["tools_done"] = 0
    _agent_state["tools_total"] = total_tools


def begin_tool(name: str):
    """Called right before a tool executes."""
    _agent_state["current_tool"] = name
    _agent_state["state"] = "working"


def end_tool(name: str):
    """Called right after a tool finishes."""
    _agent_state["tools_done"] += 1
    _agent_state["current_tool"] = ""
    hist = _agent_state["history"]
    hist.append(name)
    if len(hist) > 5:
        del hist[0]


def set_pet_action(action: str):
    """Queue a one-shot animation for the desktop pet (widget polls)."""
    _agent_state["pet_action"] = action
    _agent_state["pet_seq"] += 1
    try:
        import json as _json
        import os as _os
        path = _os.path.expanduser("~/.config/kibo/pet_action.json")
        _os.makedirs(_os.path.dirname(path), exist_ok=True)
        tmp = path + ".tmp"
        with open(tmp, "w") as f:
            _json.dump({"action": action, "seq": _agent_state["pet_seq"]}, f)
        _os.replace(tmp, path)
    except OSError:
        pass


def read_pet_action_file():
    """Read the persisted pet action (for the widget, cross-process)."""
    try:
        import json as _json
        import os as _os
        path = _os.path.expanduser("~/.config/kibo/pet_action.json")
        with open(path) as f:
            data = _json.load(f)
        return data.get("action", ""), int(data.get("seq", 0))
    except (OSError, ValueError, AttributeError):
        return "", 0


def read_pet_scroll_file():
    """Read the pending message-replay command (widget side)."""
    try:
        import json as _json
        import os as _os
        path = _os.path.expanduser("~/.config/kibo/pet_scroll.json")
        with open(path) as f:
            data = _json.load(f)
        msgs = data.get("messages", [])
        if not isinstance(msgs, list):
            msgs = []
        return int(data.get("seq", 0) or 0), [str(m) for m in msgs]
    except (OSError, ValueError, AttributeError):
        return 0, []


def start_message_scroll(messages):
    """Tell the widget to replay these messages, bottom to top."""
    try:
        import json as _json
        import os as _os
        path = _os.path.expanduser("~/.config/kibo/pet_scroll.json")
        _os.makedirs(_os.path.dirname(path), exist_ok=True)
        seq, _ = read_pet_scroll_file()
        tmp = path + ".tmp"
        with open(tmp, "w") as f:
            _json.dump({"seq": seq + 1, "messages": messages}, f)
        _os.replace(tmp, path)
        return seq + 1
    except OSError:
        return 0
