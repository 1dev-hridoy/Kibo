import time



def render_idle_card(widget, custom="", anim="fade", force=False):
    """Idle card: custom message highlighted on top with a live clock +
    system info line beneath it, or just clock + info when no message.

    The top line is only redrawn when the message actually changes, while
    the info line ticks every call, so the 1s poll and the hover handler
    never fight over the same slots.
 
       """
    hidden = getattr(widget, "_card_hidden", False)
    key = (custom, anim)
    retop = force or hidden or key != getattr(widget, "_card_key", None)



    accent = widget.cfg.get("accent_color", "#89b4fa")
    fg = widget.cfg.get("fg_color", "#cdd6f4")
    stamp = time.strftime("%H:%M")
    info = widget._sys_info()



    if retop:
        if custom:
            shown = (f"\u2665\u2665 {custom} \u2665\u2665"
                     if anim == "hearts" else custom)
            widget._shown_custom = shown
            widget._shown_raw = custom
            widget.status_label.set_style(fill=accent,
                                          font=widget._font_status)
            if force or custom != getattr(widget, "_shown_raw_before", ""):
                widget.status_label.set_animated(custom, mode=anim)
            else:
                widget.status_label.config(text=shown)


        else:
            widget._shown_custom = ""
            widget._shown_raw = ""
            widget.status_label.set_style(fill=fg,
                                          font=widget._font_status)
            widget.status_label.config(text=stamp)
        widget._shown_raw_before = custom
        widget._card_key = key
        widget._card_hidden = False



    if custom:
        widget.task_label.set_style(fill="#9399b2", font=widget._font_info)
        widget.task_label.config(text=f"{stamp} \u00b7 {info}")


    else:
        widget.task_label.set_style(fill="#9399b2", font=widget._font_info)
        widget.task_label.config(text=info)