import time


def animate_width(widget, target):
    widget._width_target = target
    if getattr(widget, "_width_animating", False):
        return
    widget._width_animating = True
    _step_width(widget)







def _step_width(widget):
    cur = widget.root.winfo_width()
    tgt = widget._width_target
    sw = widget.root.winfo_screenwidth()
    h = widget.cfg["height"]
    y = widget.cfg.get("y", 0)



    if abs(cur - tgt) <= 10:

        widget.root.geometry(f"{tgt}x{h}+{(sw - tgt) // 2}+{y}")
        widget._width_animating = False
        return
    nxt = int(cur + (tgt - cur) * 0.35)
    widget.root.geometry(f"{nxt}x{h}+{(sw - nxt) // 2}+{y}")
    widget.root.after(16, lambda: _step_width(widget))




def recenter(widget):
    if time.time() - getattr(widget, "_last_drag", 0) < 5:
        return
    sw = widget.root.winfo_screenwidth()
    w = widget.root.winfo_width()



    
    if w < 10:
        return
    cx = (sw - w) // 2
    if abs(widget.root.winfo_x() - cx) > 2:
        widget.root.geometry(f"+{cx}+{widget.cfg.get('y', 0)}")
