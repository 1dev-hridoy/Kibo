"""Replay saved widget messages one at a time, each sliding bottom to top."""
import time

HOLD = 1.6
RISE = 0.45
LIFT = 46


def _ease(t):
    return 1 - (1 - t) ** 3


def start(widget, messages):
    msgs = [str(m).strip() for m in (messages or []) if str(m).strip()]
    if not msgs:
        widget._scroll_active = False
        return False
    widget._cancel_collapse()
    widget._scroll_active = True
    widget._scroll_msgs = msgs
    widget._scroll_idx = 0
    widget._scroll_t = time.time()
    widget._scroll_last = msgs[-1]
    widget._card_hidden = False
    widget.avatar.set_state("idle")
    widget._set_expanded(True, compact=True)
    _show(widget, msgs[0])
    widget.root.after(16, lambda: _frame(widget))
    return True






def _show(widget, text):
    accent = widget.cfg.get("accent_color", "#89b4fa")
    widget.status_label.set_style(fill=accent, font=widget._font_status)
    widget.status_label.set_animated(text, mode="fade")
    widget.task_label.set_style(fill="#9399b2", font=widget._font_info)
    widget.task_label.config(
        text=f"{widget._scroll_idx + 1} / {len(widget._scroll_msgs)}")
    widget.tool_label.hide()
    widget.frame.texts[0]["dy"] = LIFT





def _frame(widget):
    if not getattr(widget, "_scroll_active", False):
        return
    now = time.time()
    el = now - widget._scroll_t
    slot = widget.frame.texts[0]
    if el < RISE:
        slot["dy"] = int(LIFT * (1 - _ease(el / RISE)))


    else:
        slot["dy"] = 0
    if el >= RISE + HOLD:
        nxt = widget._scroll_idx + 1
        if nxt >= len(widget._scroll_msgs):
            _finish(widget)
            return
        widget._scroll_idx = nxt
        widget._scroll_t = now


        _show(widget, widget._scroll_msgs[nxt])
    widget.root.after(16, lambda: _frame(widget))


def _finish(widget):
    widget._scroll_active = False
    widget.frame.texts[0]["dy"] = 0
    last = getattr(widget, "_scroll_last", "")


    widget._scroll_msgs = []
    if last:
        try:
            from agent.core.agent_state import write_pet_message
            write_pet_message(last, "fade", 0)
        except Exception:
            pass



    widget._shown_raw = ""
    widget._card_key = None
    widget._msg_collapsed = False
    widget._msg_timer_armed = False
