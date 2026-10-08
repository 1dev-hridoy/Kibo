import tkinter as tk
from agent.desktop_widget.config import save_config
from agent.desktop_widget.api import KiboAPI


def open_settings(widget):
    dlg = tk.Toplevel(widget.root)
    dlg.title("Kibo Widget Settings")
    dlg.geometry("400x430")
    dlg.configure(bg=widget.cfg["bg_color"])
    dlg.attributes("-topmost", True)

    tk.Label(dlg, text="Widget Settings", bg=widget.cfg["bg_color"],
             fg=widget.cfg["fg_color"],
             font=("Segoe UI", 12, "bold")).pack(pady=10)



    fields = [
        ("Active width:", str(widget.cfg["width"]), "width"),
        ("Idle width:", str(widget.cfg.get("idle_width", 140)), "idle_width"),
        ("Height:", str(widget.cfg.get("height", 128)), "height"),
        ("Avatar size:", str(widget.cfg.get("avatar_size", 100)), "avatar_size"),
        ("API URL:", widget.cfg["api_base"], "api_base"),
        ("Screensaver after (s):",
         str(widget.cfg.get("pixel_screensaver_seconds", 45)),
         "pixel_screensaver_seconds"),
    ]




    entries = {}
    for label, value, key in fields:
        f = tk.Frame(dlg, bg=widget.cfg["bg_color"])
        f.pack(fill="x", padx=20, pady=4)
        tk.Label(f, text=label, bg=widget.cfg["bg_color"],
                 fg=widget.cfg["fg_color"]).pack(side="left")
        var = tk.StringVar(value=value)
        tk.Entry(f, textvariable=var, width=25).pack(side="right")
        entries[key] = var




    f = tk.Frame(dlg, bg=widget.cfg["bg_color"])
    f.pack(fill="x", padx=20, pady=8)
    tk.Label(f, text="Opacity:", bg=widget.cfg["bg_color"],
             fg=widget.cfg["fg_color"]).pack(side="left")
    o_var = tk.DoubleVar(value=widget.cfg["opacity"])
    tk.Scale(f, from_=0.3, to=1.0, resolution=0.05, orient="horizontal",
             variable=o_var, bg=widget.cfg["bg_color"], fg=widget.cfg["fg_color"],
             highlightthickness=0).pack(side="right", fill="x", expand=True)



    def save():
        widget.cfg["width"] = int(entries["width"].get())
        widget.cfg["idle_width"] = int(entries["idle_width"].get())
        widget.cfg["height"] = int(entries["height"].get())
        widget.cfg["avatar_size"] = int(entries["avatar_size"].get())
        widget.cfg["api_base"] = entries["api_base"].get()
        widget.cfg["pixel_screensaver_seconds"] = \
            int(entries["pixel_screensaver_seconds"].get())
        widget.cfg["opacity"] = o_var.get()




        avatar = widget.cfg["avatar_size"]
        if widget.cfg["height"] < avatar + 24:
            widget.cfg["height"] = avatar + 24
        if widget.cfg["idle_width"] < avatar + 36:
            widget.cfg["idle_width"] = avatar + 36
        if widget.cfg["width"] < widget.cfg["idle_width"] + 320:
            widget.cfg["width"] = widget.cfg["idle_width"] + 580

        save_config(widget.cfg)
        widget.root.attributes("-alpha", widget.cfg["opacity"])

        new_size = widget.cfg["avatar_size"]
        widget.avatar.size = new_size



        widget._w_idle = widget.cfg["idle_width"]
        widget._w_active = widget.cfg["width"]
        widget._expanded = None
        widget._set_expanded(widget._last_state != "idle"
                           and widget._last_state is not None)
        widget.api = KiboAPI(widget.cfg["api_base"])
        dlg.destroy()




    tk.Button(dlg, text="Save", command=save,
              bg=widget.cfg["accent_color"], fg="#1e1e2e",
              font=("Segoe UI", 10, "bold")).pack(pady=15)

