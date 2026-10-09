def render_task_card(widget, state, task, custom, tool, done, total, history):
    """Working / approval card: status line, task line and tool line."""
    if state == "working":
        status_text = "Working..."
        task_text = task[:70] if task else (custom[:70] if custom else "")
    else:
        status_text = "⚠ Needs approval"
        task_text = task[:70] if task else (custom[:70] if custom
                                            else "Your input required")




    if state != widget._last_state:
        widget.status_label.set_animated(status_text)
        if task_text:
            widget.task_label.set_animated(task_text, delay_ms=120)
        else:
            widget.task_label.hide()
    elif task_text:
        widget.task_label.config(text=task_text)






    if tool:
        progress = f" [{done}/{total}]" if total > 1 else ""
        tool_text = f"⚙ {tool}{progress}"
        widget.tool_label.set_animated(tool_text, delay_ms=60)
    elif history:
        widget.tool_label.config(
            text=f"✓ {history[-1]} ({done}/{total})")
    else:
        widget.tool_label.hide()
