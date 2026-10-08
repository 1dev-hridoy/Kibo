"""
Needle agent initialization and engine loop.
Supports switching between Needle and FunctionGemma.
"""

import difflib
import json
import os
import re
import threading

from agent.tools import ALL_TOOLS
from agent.model_manager import create_backend, get_active_model, MODELS
from .prompt import _strip_meta, _fallback
from .sandbox import check_command_safety, SandboxError
from agent.core.agent_state import update_agent_state, begin_task, begin_tool, end_tool


def _init_backend():
    """Initialize the model backend based on active model selection."""
    model = get_active_model()
    info = MODELS.get(model, {})
    print(f"Loading {info.get('name', model)} model...")
    backend = create_backend(ALL_TOOLS)
    print(f"Agent ready — {len(ALL_TOOLS)} tools registered.")
    return backend


def _enrich_tool_docs():
    """Append rich usage context to every tool docstring so the small model
    routes user phrasing to the right function."""
    for fn in ALL_TOOLS:
        name = fn.__name__
        words = name.replace("_", " ")
        rest = words
        for verb in ("get ", "set ", "take ", "make ", "do ", "check ", "show ", "list ", "open ", "run ", "read ", "write ", "play ", "send ", "lock ", "scan "):
            if words.startswith(verb):
                rest = words[len(verb):]
                break
        phrases = {words} if words == rest else {words, rest}
        doc = (fn.__doc__ or "").strip()
        if "Context for routing" in doc:
            continue
        hints = ", ".join(f'"{p}"' for p in sorted(phrases))
        fn.__doc__ = (doc + f"\nAlso called: {hints}.").strip()


_enrich_tool_docs()


_tools = {fn.__name__: fn for fn in ALL_TOOLS}
_tool_names = list(_tools)

_engine_lock = threading.Lock()


def reload_backend():
    """Reload the model backend (after switching models)."""
    global _backend
    _backend = _init_backend()
    return _backend


_backend = _init_backend()

try:
    if not os.environ.get("KIBO_NO_REMINDERS"):
        from agent.runner.reminders import ensure_jobs
        ensure_jobs()
except Exception:
    pass
try:
    if not os.environ.get("KIBO_NO_REMINDERS"):
        from agent.tools.briefing_tools import ensure_briefing_job
        ensure_briefing_job()
except Exception:
    pass


def _agent_loop(text, max_steps=4):
    """Drive the engine with a hallucination guard: calls scoring below
    the confidence threshold are never executed (tiny models emit
    plausible-looking but spurious calls on small talk)."""
    begin_task(text[:60])
    _backend.reset()
    response = _backend.complete(text)
    executed, results = [], []
    for _ in range(max_steps):
        calls = response.get("function_calls") or []
        conf = response.get("confidence") or 0.0
        if response.get("type") != "call" or not calls or conf < 0.15:
            break
        results = []
        for c in calls:
            name, args = c.get("name"), c.get("arguments") or {}
            if name not in _tools:
                close = difflib.get_close_matches(name or "", _tool_names, n=1, cutoff=0.72)
                name = close[0] if close else None
            executed.append({"name": name or c.get("name"), "arguments": args})
            if not name:
                results.append(f"Error: unknown tool '{c.get('name')}'")
                continue
            fn = _tools[name]


        
            if name in ("remote_terminal", "remote_terminal_background"):
                cmd = args.get("command", "")
                danger = check_command_safety(cmd)
                if danger:
                    results.append(danger)
                    continue

                
            begin_tool(name)
            try:
                results.append(str(fn(**args)))
            except SandboxError as exc:
                results.append(f"Sandbox: {exc}")
            except Exception as exc:
                results.append(f"Error: {exc}")
            finally:
                end_tool(name)
        _backend.reset()
        response = _backend.complete(json.dumps(results))
    return response, executed, results


def _extract(response, results=None):
    """Convert the final engine envelope into (text, calls)."""
    calls = response.get("function_calls") or []
    conf = response.get("confidence") or 0.0
    text = _strip_meta(response.get("reasoning") or "")

    if response.get("type") == "call" and calls and conf < 0.15:
        return (text or _fallback()), []

    if not text and results:
        text = _strip_meta("\n".join(str(r) for r in results))
    if not text:
        text = _fallback()
    update_agent_state("idle", "")
    return text, calls


def _detect_media(calls, results):
    """Detect if a screenshot or photo was taken and return its path."""
    for c in calls:
        name = c.get("name", "")
        if name in ("take_screenshot_now", "take_camera_photo"):
            for r in results:
                r = str(r)
                for prefix in ("Screenshot saved to ", "Photo saved to "):
                    if prefix in r:
                        path = r.split(prefix, 1)[1].strip()
                        kind = "screenshot" if "screenshot" in name else "photo"
                        if os.path.exists(path):
                            return {"type": kind, "path": path}
    return None
