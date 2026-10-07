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
    "_idle_since": 0.0,        
}


def get_agent_state():
    return _agent_state


def set_widget_message(message: str):
    """Set a custom message shown in the desktop widget."""
    _agent_state["custom_message"] = message[:80]


def clear_widget_message():
    _agent_state["custom_message"] = ""


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
