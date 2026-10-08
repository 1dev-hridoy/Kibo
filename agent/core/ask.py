"""
Public entry point for the agent — the ask() function.
"""

from datetime import datetime
from .engine import _engine_lock, _tools, _agent_loop, _extract, _detect_media, reload_backend
from . import fastpath as _fp
from .smalltalk import _smalltalk
from .context import add_exchange, get_context_string, get_last_topic, get_current_task
from .memory import reflect_on_exchange
from agent.model_manager import (
    switch_model, get_models_display, get_active_model,
    resolve_model_name, is_model_available, MODELS
)


def ask(text: str) -> dict:
    """Answer a user message.

    Returns {"text": <reply>, "tool_calls": [...], "results": [...],
             "media": {"type": "screenshot", "path": "..."} or None}.
    """
    with _engine_lock:
        chat_reply = _smalltalk(text)
        if chat_reply:
            add_exchange(text, chat_reply)
            return {"text": chat_reply, "tool_calls": [], "results": [],
                    "media": None}

        spec = _fp._fastpath(text)

        # ── Model management commands ──────────────────────────────────
        if isinstance(spec, tuple) and spec[0] == "__switch_model__":
            _, model_name = spec
            current = get_active_model()
            current_name = MODELS.get(current, {}).get("name", current)

            resolved = resolve_model_name(model_name)

            # If they typed just the model name (not "switch X"), show status
            if model_name == resolved:
                if resolved == current:


                    reply = (


                        f"Current model: {current_name}\n"
                        f"Already using this model.\n"
                        f"Type 'gemma' or 'needle' to switch."
                    )
                    add_exchange(text, reply)
                    reflect_on_exchange(text, reply)
                    return {


                        "text": reply,


                        "tool_calls": [], "results": [], "media": None
                    }
                if not is_model_available(resolved):
                    target_name = MODELS.get(resolved, {}).get("name", resolved)
                    reply = (
                        f"Current model: {current_name}\n"
                        f"Target model: {target_name} (not downloaded)\n"
                        f"Run: ./install.sh --fresh to download it."
                    )


                    add_exchange(text, reply)
                    reflect_on_exchange(text, reply)
                    return {

                        "text": reply,
                        "tool_calls": [], "results": [], "media": None
                    }

            success, msg = switch_model(model_name)
            if success:
                reload_backend()
                from agent.model_manager import get_active_model as _active
                if _active() != resolve_model_name(model_name):
                    msg = (msg + "\nNote: the new backend could not load, "
                           "still running on the previous model.")
            add_exchange(text, msg)


            reflect_on_exchange(text, msg)


            return {"text": msg, "tool_calls": [], "results": [],
                    "media": None}

        if isinstance(spec, tuple) and spec[0] == "__models__":
            reply = get_models_display()
            add_exchange(text, reply)


            reflect_on_exchange(text, reply)


            return {"text": reply, "tool_calls": [],
                    "results": [], "media": None}

        if isinstance(spec, tuple) and spec[0] == "__current_model__":
            current = get_active_model()
            info = MODELS.get(current, {})
            reply = (
                f"Current model: {info.get('name', current)}\n"
                f"Maker: {info.get('maker', 'Unknown')}\n"
                f"Size: {info.get('size', 'Unknown')}\n"
                f"Type 'models' to see all options."
            )
            add_exchange(text, reply)
            
            reflect_on_exchange(text, reply)
            return {
                "text": reply,
                "tool_calls": [], "results": [], "media": None
            }

        if spec == "clock":
            reply = datetime.now().strftime("It's %I:%M %p.")
            add_exchange(text, reply)
            reflect_on_exchange(text, reply)
            return {"text": reply,
                    "tool_calls": [], "results": [], "media": None}
        if spec == "date":
            reply = datetime.now().strftime("Today is %A, %B %d, %Y.")
            add_exchange(text, reply)
            reflect_on_exchange(text, reply)
            return {"text": reply,
                    "tool_calls": [], "results": [], "media": None}
        if isinstance(spec, tuple) and spec[0] == "__reply__":
            reply = spec[1]
            add_exchange(text, reply)
            reflect_on_exchange(text, reply)
            return {"text": reply,
                    "tool_calls": [], "results": [], "media": None}
        if spec is not None:
            executed, outs = [], []
            for name, args in spec:
                executed.append({"name": name, "arguments": args})
                try:
                    outs.append(str(_tools[name](**args)))
                except Exception as exc:
                    outs.append(f"Error: {exc}")
            for e in executed:
                if e["name"] == "set_volume":
                    _fp._last_topic = "volume"
                elif e["name"] == "set_screen_brightness":
                    _fp._last_topic = "brightness"
            media = _detect_media(executed, outs)
            reply = "\n".join(outs)
            add_exchange(text, reply, executed, outs)
            reflect_on_exchange(text, reply, executed)
            return {"text": reply, "tool_calls": executed,
                    "results": outs, "media": media}

        response, executed, results = _agent_loop(text)
        reply, calls = _extract(response, results)
        media = _detect_media(
            [{"name": c.get("name"), "arguments": c.get("arguments") or {}}
             for c in calls] if calls else executed, results)
        add_exchange(text, reply, executed, results)
        reflect_on_exchange(text, reply, executed)
        return {"text": reply,
                "tool_calls": [{"name": c.get("name"),
                                "arguments": c.get("arguments") or {}}
                               for c in calls] if calls else executed,
                "results": results, "media": media}
