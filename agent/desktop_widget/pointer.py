import time


def pet_at(widget, event):
    try:
        return widget.avatar.hover_at(event.x, event.y)
    except Exception:
        return False

    

def start_drag(widget, event):
    if pet_at(widget, event):
        widget.avatar.click_at(event.x, event.y)

        widget._drag_x = None
        widget._drag_y = None
        return

    
    widget._drag_x = event.x
    widget._drag_y = event.y



def on_motion(widget, event):
    if pet_at(widget, event):
        return

    
    if widget._last_seen_state == "idle":
        widget._peek_until = time.time() + 12
        widget.status_label.config(
            text=time.strftime("%H:%M"))
        widget.task_label.config(text=widget._sys_info())



        widget.tool_label.hide()

def on_leave(widget, event):
    try:
        widget.avatar.hover_at(-1, -1)



    except Exception:
        pass
    if widget._last_seen_state == "idle":
        widget._peek_until = min(widget._peek_until, time.time() + 7)

