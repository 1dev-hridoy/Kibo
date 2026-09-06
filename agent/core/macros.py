"""
Macro recording — record and replay sequences of actions.
"""

import os
import json
import time
import threading

MACROS_DIR = os.path.expanduser("~/.kibo_macros")
_recording = None
_recorded_steps = []
_record_lock = threading.Lock()


def _ensure_dir():
    """Ensure macros directory exists."""
    os.makedirs(MACROS_DIR, exist_ok=True)


def _macro_path(name):
    """Get path for a macro file."""
    safe = name.replace("/", "_").replace(" ", "_").lower()
    return os.path.join(MACROS_DIR, f"{safe}.json")


def start_recording(name):
    """Start recording a macro."""
    global _recording, _recorded_steps
    with _record_lock:
        if _recording:
            return f"Already recording: {_recording}"
        _recording = name
        _recorded_steps = []
        return f"Recording macro: {name}"


def record_step(tool_name, arguments, result=""):
    """Record a step in the current macro."""
    global _recorded_steps
    with _record_lock:
        if not _recording:
            return
        _recorded_steps.append({
            "tool": tool_name,
            "args": arguments,
            "result": str(result)[:200],
            "timestamp": time.time(),
        })


def stop_recording(save=True):
    """Stop recording and optionally save."""
    global _recording, _recorded_steps
    with _record_lock:
        if not _recording:
            return "Not recording"
        name = _recording
        steps = _recorded_steps.copy()
        _recording = None
        _recorded_steps = []

        if save and steps:
            save_macro(name, steps)
            return f"Saved macro '{name}' with {len(steps)} steps"
        return f"Discarded macro '{name}'"


def save_macro(name, steps):
    """Save a macro to disk."""
    _ensure_dir()
    path = _macro_path(name)
    macro = {
        "name": name,
        "steps": steps,
        "created": time.time(),
        "step_count": len(steps),
    }
    with open(path, "w") as f:
        json.dump(macro, f, indent=2)


def load_macro(name):
    """Load a macro from disk."""
    path = _macro_path(name)
    if not os.path.exists(path):
        return None
    with open(path) as f:
        return json.load(f)


def list_macros():
    """List all saved macros."""
    _ensure_dir()
    macros = []
    for f in os.listdir(MACROS_DIR):
        if f.endswith(".json"):
            path = os.path.join(MACROS_DIR, f)
            try:
                with open(path) as fh:
                    m = json.load(fh)
                    macros.append({
                        "name": m.get("name", f[:-5]),
                        "steps": m.get("step_count", len(m.get("steps", []))),
                        "created": m.get("created", 0),
                    })
            except Exception:
                pass

    if not macros:
        return "No macros saved"

    result = "Saved macros:\n"
    for m in macros:
        result += f"  - {m['name']} ({m['steps']} steps)\n"
    return result


def delete_macro(name):
    """Delete a macro."""
    path = _macro_path(name)
    if os.path.exists(path):
        os.remove(path)
        return f"Deleted macro: {name}"
    return f"Macro not found: {name}"


def replay_macro(name):
    """Replay a macro by executing its steps."""
    macro = load_macro(name)
    if not macro:
        return f"Macro not found: {name}"

    from agent.core.ask import ask
    results = []
    for i, step in enumerate(macro.get("steps", [])):
        tool = step.get("tool", "")
        args = step.get("args", {})
        try:
            # Build a command string for the agent
            cmd = f"run {tool}"
            if args:
                arg_str = ", ".join(f"{k}={v}" for k, v in args.items())
                cmd += f" with {arg_str}"
            result = ask(cmd)
            results.append(f"Step {i+1}: {tool} -> OK")
        except Exception as e:
            results.append(f"Step {i+1}: {tool} -> Error: {e}")

    return f"Replayed '{name}': {len(results)} steps\n" + "\n".join(results)


def get_recording_status():
    """Get current recording status."""
    with _record_lock:
        if _recording:
            return f"Recording: {_recording} ({len(_recorded_steps)} steps)"
        return "Not recording"
