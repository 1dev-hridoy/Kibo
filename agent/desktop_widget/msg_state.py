"""Collapse / auto-expiry helpers for the desktop widget card."""


def cancel_collapse(widget):
    widget._msg_timer_armed = False
    if widget._collapse_after:
        try:
            widget.root.after_cancel(widget._collapse_after)


        except Exception:
            pass
        widget._collapse_after = None


def schedule_collapse(widget, ms):
    cancel_collapse(widget)
    widget._collapse_after = widget.root.after(
        ms, lambda: collapse(widget))

    


def collapse(widget):
    widget._collapse_after = None
    widget._msg_timer_armed = False
    if widget._cur_custom:

        
        widget._msg_collapsed = True
    widget._card_hidden = True
    widget.status_label.hide()
    widget.task_label.hide()
    widget.tool_label.hide()
    widget._set_expanded(False)


def expire_custom(widget, msg=None):
    if msg is not None and msg != getattr(widget, "_shown_raw", ""):
        return
    if widget._last_seen_state != "idle":
        widget.root.after(5000,
                          lambda: expire_custom(widget, msg))


        
        return
    try:
        from agent.core.agent_state import clear_widget_message
        clear_widget_message()


    except Exception:



        pass
    try:
        import os
        p = os.path.expanduser("~/.config/kibo/pet_message.json")
        if os.path.exists(p):
            os.remove(p)


    except OSError:
        pass
    collapse(widget)


def merge_shared_files(widget, status):
    """Fold in pet action / message / replay files written by other
    processes, and flag a freshly (re)set message."""
    try:
        from agent.core.agent_state import read_pet_action_file
        faction, fseq = read_pet_action_file()
        if fseq > status.get("pet_seq", 0):
            status["pet_action"] = faction
            status["pet_seq"] = fseq



        if not status.get("custom_message"):
            from agent.core.agent_state import read_pet_message_file
            fmsg, fanim, fexp = read_pet_message_file()
            if fmsg:
                status["custom_message"] = fmsg
                status["custom_animation"] = fanim
                status["custom_expires_in"] = fexp



    except Exception:
        pass
    try:
        import os as _os
        path = _os.path.expanduser("~/.config/kibo/pet_message.json")
        if _os.path.exists(path):
            mt = _os.path.getmtime(path)
            if mt != widget._msg_mtime:


               
                widget._msg_mtime = mt
                widget._msg_collapsed = False
                widget._msg_timer_armed = False



    except OSError:
        pass
    try:
        from agent.core.agent_state import read_pet_scroll_file
        sseq, smsgs = read_pet_scroll_file()
        if sseq != widget._scroll_seq and smsgs:
            widget._scroll_seq = sseq
            widget._pending_scroll = list(smsgs)
    except Exception:
        pass
