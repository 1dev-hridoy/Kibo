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
    "pet_action": "",
    "pet_seq": 0,
    "_idle_since": 0.0,        
}


def get_agent_state():
    return _agent_state


def set_widget_message(message: str, animation: str = "fade"):
    """Set a custom message shown in the desktop widget."""
    _agent_state["custom_message"] = message[:80]
    _agent_state["custom_animation"] = animation or "fade"
    try:
        import json as _json
        import os as _os
        path = _os.path.expanduser("~/.config/kibo/pet_message.json")
        _os.makedirs(_os.path.dirname(path), exist_ok=True)
        tmp = path + ".tmp"
        with open(tmp, "w") as f:
            _json.dump({"message": message[:80],
                        "animation": animation or "fade"}, f)
        _os.replace(tmp, path)
    except OSError:
        pass


def read_pet_message_file():
    try:
        import json as _json
        import os as _os
        path = _os.path.expanduser("~/.config/kibo/pet_message.json")
        with open(path) as f:
            data = _json.load(f)
        return data.get("message", ""), data.get("animation", "fade")
    except (OSError, ValueError, AttributeError):
        return "", "fade"


def clear_widget_message():
    _agent_state["custom_message"] = ""
    _agent_state["custom_animation"] = "fade"
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
