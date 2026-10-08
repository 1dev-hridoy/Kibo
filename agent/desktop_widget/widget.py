import threading
import time
import tkinter as tk

from agent.desktop_widget.config import load_config, save_config
from agent.desktop_widget.api import KiboAPI
from agent.desktop_widget.space_bg import SpaceBackground
from agent.desktop_widget.avatar import MochiAvatar


class AnimLabel(tk.Label):
    def __init__(self, parent, bg, fg, **kwargs):
        super().__init__(parent, bg=bg, fg=fg, **kwargs)
        self._target_fg = fg
        self._bg = bg
        self._anim_id = None

    def set_animated(self, text, delay_ms=0, mode="fade"):
        if self._anim_id:
            try:
                self.after_cancel(self._anim_id)
            except Exception:
                pass
        self.config(text="")
        if mode == "type":
            self.after(delay_ms or 0, lambda: self._typewriter(text, 0))
        elif mode == "hearts":
            self.after(delay_ms or 0, lambda: self._hearts_fade(f"♥♥ {text} ♥♥", 0))
        else:
            if delay_ms:
                self.after(delay_ms, lambda: self._fade_in(text, 0))
            else:
                self._fade_in(text, 0)

    def _typewriter(self, text, i):
        if i > len(text):
            return
        self.config(text=text[:i])
        self._anim_id = self.after(35, lambda: self._typewriter(text, i + 1))



    def _hearts_fade(self, text, step):
        self.config(text=text)
        steps = 9
        if step >= steps:
            return

        
        try:
            r2 = int("#f38ba8"[1:3], 16); g2 = int("#f38ba8"[3:5], 16); b2 = int("#f38ba8"[5:7], 16)
            r1 = int(self._bg[1:3], 16); g1 = int(self._bg[3:5], 16); b1 = int(self._bg[5:7], 16)
            t = step / steps
            r = int(r1 + (r2 - r1) * t); g = int(g1 + (g2 - g1) * t); b = int(b1 + (b2 - b1) * t)
            self.config(fg=f"#{r:02x}{g:02x}{b:02x}")
        except (ValueError, IndexError):
            self.config(fg="#f38ba8")
        self._anim_id = self.after(50, lambda: self._hearts_fade(text, step + 1))

    def _fade_in(self, text, step):
        self.config(text=text)
        steps = 9
        if step >= steps:
            self.config(fg=self._target_fg)
            return
        try:
            r1 = int(self._bg[1:3], 16); g1 = int(self._bg[3:5], 16); b1 = int(self._bg[5:7], 16)
            r2 = int(self._target_fg[1:3], 16); g2 = int(self._target_fg[3:5], 16); b2 = int(self._target_fg[5:7], 16)
            t = step / steps
            r = int(r1 + (r2 - r1) * t)
            g = int(g1 + (g2 - g1) * t)
            b = int(b1 + (b2 - b1) * t)
            self.config(fg=f"#{r:02x}{g:02x}{b:02x}")
        except (ValueError, IndexError):
            self.config(fg=self._target_fg)
        self._anim_id = self.after(45, lambda: self._fade_in(text, step + 1))

    def set_bg(self, color):
        self._bg = color
        self.config(bg=color)

    def hide(self):
        if self._anim_id:
            try:
                self.after_cancel(self._anim_id)
            except Exception:
                pass
        self.config(text="")


class KiboWidget:
    def __init__(self):
        self.cfg = load_config()
        self.api = KiboAPI(self.cfg["api_base"])
        self.running = True
        self._expanded = False
        self._last_state = None
        self._last_pet_seq = 0
        self._drag_x = None
        self._drag_y = None
        self._idle_seconds = 0
        self._setup_window()
        self._setup_ui()
        self._start_poller()

    def _setup_window(self):
        self.root = tk.Tk()
        self.root.title("Kibo")
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.attributes("-alpha", self.cfg["opacity"])

        sw = self.root.winfo_screenwidth()
        self._w_idle = self.cfg.get("idle_width", 140)
        self._w_active = self.cfg["width"]
        x = (sw - self._w_idle) // 2
        y = self.cfg.get("y", 0)
        self.root.geometry(f"{self._w_idle}x{self.cfg['height']}+{x}+{y}")
        self.root.configure(bg=self.cfg["bg_color"])

        self.root.bind("<Button-3>", self._show_menu)
        self.root.bind("<Double-Button-1>", lambda e: self._open_web_ui())
        self.root.bind("<Button-1>", self._start_drag)
        self.root.bind("<B1-Motion>", self._do_drag)

    def _start_drag(self, event):
        if event.widget is self.avatar:
            return
        self._drag_x = event.x
        self._drag_y = event.y

    def _do_drag(self, event):
        if self._drag_x is None:
            return
        x = self.root.winfo_x() + event.x - self._drag_x
        y = self.root.winfo_y() + event.y - self._drag_y
        self.root.geometry(f"+{x}+{y}")

    def _setup_ui(self):
        bg = self.cfg["bg_color"]
        fg = self.cfg["fg_color"]
        fs = self.cfg["font_size"]

        self.frame = SpaceBackground(self.root, base_color=bg, bg=bg)
        self.frame.pack(fill="both", expand=True)

        avatar_size = self.cfg.get("avatar_size", 100)
        self.avatar = MochiAvatar(self.frame, size=avatar_size,
                                   bg=bg, base_bg=bg)
        self.avatar.pack(expand=True)

        self.text_frame = tk.Frame(self.frame, bg=bg)
        self._space_top = tk.Frame(self.text_frame, bg=bg)
        self._space_top.pack(fill="x", expand=True)

        self.status_label = AnimLabel(self.text_frame, bg=bg, fg=fg,
                                       font=("Segoe UI", fs, "bold"),
                                       anchor="w")
        self.status_label.pack(fill="x")

        self.task_label = AnimLabel(self.text_frame, bg=bg, fg="#9399b2",
                                     font=("Segoe UI", fs - 1), anchor="w")
        self.task_label.pack(fill="x", pady=1)

        self.tool_label = AnimLabel(self.text_frame, bg=bg,
                                     fg=self.cfg.get("tool_color", "#94e2d5"),
                                     font=("Consolas", fs - 2), anchor="w")
        self.tool_label.pack(fill="x", pady=1)
        self._space_bottom = tk.Frame(self.text_frame, bg=bg)
        self._space_bottom.pack(fill="x", expand=True)

        self.model_var = tk.StringVar(value="")
        self.model_label = tk.Label(self.frame, textvariable=self.model_var,
                                     bg=self.cfg["accent_color"], fg="#1e1e2e",
                                     font=("Segoe UI", fs - 1, "bold"), padx=6)

    def _set_expanded(self, expanded: bool):
        if expanded == self._expanded:
            return
        self._expanded = expanded
        sw = self.root.winfo_screenwidth()
        h = self.cfg["height"]
        if expanded:
            w = self._w_active
            self.avatar.pack(side="left", padx=(18, 12), pady=8)
            self.text_frame.pack(side="left", fill="both", expand=True,
                                  pady=(6, 6))
            self.model_label.pack(side="right", padx=(8, 0))
        else:
            w = self._w_idle
            self.avatar.pack(expand=True)
            self.text_frame.pack_forget()
            self.model_label.pack_forget()
            self.status_label.hide()
            self.task_label.hide()
            self.tool_label.hide()
        x = (sw - w) // 2
        self.root.geometry(f"{w}x{h}+{x}+{self.cfg.get('y', 0)}")

    def _start_poller(self):
        def poll():
            while self.running:
                self._fetch_status()
                time.sleep(self.cfg["poll_interval"])
        threading.Thread(target=poll, daemon=True).start()

    def _fetch_status(self):
        model_info = self.api.get_model()
        if "active" in model_info:
            name = model_info.get("name", model_info["active"])
            self.root.after(0, lambda: self.model_var.set(f" {name} "))
        status = self.api.get_status()
        if "error" in status:
            status = {"state": "idle", "current_task": "", "current_tool": "",
                      "tools_done": 0, "tools_total": 0, "history": [],
                      "custom_message": "", "_idle_since": 0}
 
 
        try:
            from agent.core.agent_state import read_pet_action_file
            faction, fseq = read_pet_action_file()
            if fseq > status.get("pet_seq", 0):
                status["pet_action"] = faction
                status["pet_seq"] = fseq
            if not status.get("custom_message"):
                from agent.core.agent_state import read_pet_message_file
                fmsg, fanim = read_pet_message_file()
                if fmsg:
                    status["custom_message"] = fmsg
                    status["custom_animation"] = fanim
        except Exception:
            pass
        self.root.after(0, lambda: self._apply_status(status))

    def _apply_status(self, status):
        state = status.get("state", "idle")
        task = status.get("current_task", "")
        tool = status.get("current_tool", "")
        done = status.get("tools_done", 0)
        total = status.get("tools_total", 0)
        history = status.get("history", [])
        custom = status.get("custom_message", "")
        custom_anim = status.get("custom_animation", "fade")
        pet_action = status.get("pet_action", "")
        pet_seq = status.get("pet_seq", 0)
        if pet_seq != self._last_pet_seq:
            self._last_pet_seq = pet_seq
            self.avatar.trigger(pet_action)

        idle_since = status.get("_idle_since", 0)
        recently_active = state != "idle" or (time.time() - idle_since) < 3.0
        is_active = state != "idle" or bool(custom) or recently_active

        if state == "idle" and not custom and not recently_active:
            self._idle_seconds += self.cfg["poll_interval"]
        else:
            self._idle_seconds = 0

        screensaver_sec = self.cfg.get("pixel_screensaver_seconds", 45)
        if self._idle_seconds >= screensaver_sec and state == "idle":
            self.avatar.set_mode("pixel")
            self.frame.set_state_tint("pixel")
        else:
            self.avatar.set_mode("mochi")
            self.frame.set_state_tint(state)

        self._sync_text_bg()

        if state == "idle" and recently_active and \
           self._last_state in ("working", "custom"):
            self.avatar.celebrate()

        self._set_expanded(is_active)

        if state == "idle" and not custom and not recently_active:
            self.avatar.set_state("sleepy" if self._idle_seconds > 20 else "idle")
            self._last_state = "idle"
            return

        if state == "idle" and not custom and recently_active:
            self.avatar.set_state("idle")
            if self._last_state != "idle" and not self.avatar._confetti:
                self.status_label.set_animated("Done!")
                if history:
                    self.tool_label.set_animated(f"✓ {history[-1]}", delay_ms=100)
                else:
                    self.task_label.set_animated("Task completed", delay_ms=100)
            self._last_state = "idle"
            return

        if custom and state == "idle":
            self.avatar.set_state("working")
            if self._last_state != "custom":
                self.status_label.set_animated(custom, mode=custom_anim)
                self.task_label.hide()
                self.tool_label.hide()
            else:
                self.status_label.config(text=custom)
            self._last_state = "custom"
            return

        self.avatar.set_state(state)

        if state == "working":
            status_text = "Working..."
            task_text = custom if custom else (task[:70] if task else "")
        else:
            status_text = "⚠ Needs approval"
            task_text = custom if custom else (task[:70] if task else "Your input required")

        if state != self._last_state:
            self.status_label.set_animated(status_text)
            if task_text:
                self.task_label.set_animated(task_text, delay_ms=120)
            else:
                self.task_label.hide()
        elif task_text:
            self.task_label.config(text=task_text)

        if tool:
            progress = f" [{done}/{total}]" if total > 1 else ""
            tool_text = f"⚙ {tool}{progress}"
            self.tool_label.set_animated(tool_text, delay_ms=60)
        elif history:
            last = history[-1]
            self.tool_label.config(text=f"✓ {last} ({done}/{total})")
        else:
            self.tool_label.hide()

        self._last_state = state

    def _sync_text_bg(self):
        color = self.frame.base_hex()
        self.text_frame.config(bg=color)
        self._space_top.config(bg=color)
        self._space_bottom.config(bg=color)
        for lbl in (self.status_label, self.task_label, self.tool_label):
            lbl.set_bg(color)

    def _show_menu(self, event):
        menu = tk.Menu(self.root, tearoff=0, bg="#1e1e2e", fg="#cdd6f4",
                       activebackground="#313244", activeforeground="#cdd6f4")
        menu.add_command(label="Open Web UI", command=self._open_web_ui)
        menu.add_separator()
        menu.add_command(label="Lock Screen",
                         command=lambda: self.api.chat("lock screen"))
        menu.add_command(label="Volume +10%",
                         command=lambda: self.api.chat("set volume to +10"))
        menu.add_command(label="Volume -10%",
                         command=lambda: self.api.chat("set volume to -10"))
        menu.add_command(label="Screenshot",
                         command=lambda: self.api.chat("take screenshot"))
        menu.add_command(label="Pet Kibo",
                         command=lambda: self.avatar.celebrate())
        menu.add_separator()
        menu.add_command(label="Settings...", command=self._open_settings)
        menu.add_separator()
        menu.add_command(label="Quit", command=self._quit)
        menu.tk_popup(event.x_root, event.y_root)

    def _open_web_ui(self):
        import webbrowser
        scheme = "https" if self.cfg["api_base"].startswith("https") else "http"
        host = self.cfg["api_base"].replace("http://", "").replace("https://", "")
        webbrowser.open(f"{scheme}://{host}")

    def _open_settings(self):
        dlg = tk.Toplevel(self.root)
        dlg.title("Kibo Widget Settings")
        dlg.geometry("400x430")
        dlg.configure(bg=self.cfg["bg_color"])
        dlg.attributes("-topmost", True)

        tk.Label(dlg, text="Widget Settings", bg=self.cfg["bg_color"],
                 fg=self.cfg["fg_color"],
                 font=("Segoe UI", 12, "bold")).pack(pady=10)

        fields = [
            ("Active width:", str(self.cfg["width"]), "width"),
            ("Idle width:", str(self.cfg.get("idle_width", 140)), "idle_width"),
            ("Height:", str(self.cfg.get("height", 128)), "height"),
            ("Avatar size:", str(self.cfg.get("avatar_size", 100)), "avatar_size"),
            ("API URL:", self.cfg["api_base"], "api_base"),
            ("Screensaver after (s):",
             str(self.cfg.get("pixel_screensaver_seconds", 45)),
             "pixel_screensaver_seconds"),
        ]
        entries = {}
        for label, value, key in fields:
            f = tk.Frame(dlg, bg=self.cfg["bg_color"])
            f.pack(fill="x", padx=20, pady=4)
            tk.Label(f, text=label, bg=self.cfg["bg_color"],
                     fg=self.cfg["fg_color"]).pack(side="left")
            var = tk.StringVar(value=value)
            tk.Entry(f, textvariable=var, width=25).pack(side="right")
            entries[key] = var

        f = tk.Frame(dlg, bg=self.cfg["bg_color"])
        f.pack(fill="x", padx=20, pady=8)
        tk.Label(f, text="Opacity:", bg=self.cfg["bg_color"],
                 fg=self.cfg["fg_color"]).pack(side="left")
        o_var = tk.DoubleVar(value=self.cfg["opacity"])
        tk.Scale(f, from_=0.3, to=1.0, resolution=0.05, orient="horizontal",
                 variable=o_var, bg=self.cfg["bg_color"], fg=self.cfg["fg_color"],
                 highlightthickness=0).pack(side="right", fill="x", expand=True)

        def save():
            self.cfg["width"] = int(entries["width"].get())
            self.cfg["idle_width"] = int(entries["idle_width"].get())
            self.cfg["height"] = int(entries["height"].get())
            self.cfg["avatar_size"] = int(entries["avatar_size"].get())
            self.cfg["api_base"] = entries["api_base"].get()
            self.cfg["pixel_screensaver_seconds"] = \
                int(entries["pixel_screensaver_seconds"].get())
            self.cfg["opacity"] = o_var.get()

            avatar = self.cfg["avatar_size"]
            if self.cfg["height"] < avatar + 24:
                self.cfg["height"] = avatar + 24
            if self.cfg["idle_width"] < avatar + 36:
                self.cfg["idle_width"] = avatar + 36
            if self.cfg["width"] < self.cfg["idle_width"] + 320:
                self.cfg["width"] = self.cfg["idle_width"] + 580

            save_config(self.cfg)
            self.root.attributes("-alpha", self.cfg["opacity"])

            new_size = self.cfg["avatar_size"]
            self.avatar.size = new_size
            self.avatar.config(width=new_size, height=new_size)

            self._w_idle = self.cfg["idle_width"]
            self._w_active = self.cfg["width"]
            self._expanded = None
            self._set_expanded(self._last_state != "idle"
                               and self._last_state is not None)
            self.api = KiboAPI(self.cfg["api_base"])
            dlg.destroy()

        tk.Button(dlg, text="Save", command=save,
                  bg=self.cfg["accent_color"], fg="#1e1e2e",
                  font=("Segoe UI", 10, "bold")).pack(pady=15)

    def _quit(self):
        self.running = False
        self.root.destroy()

    def run(self):
        self.root.mainloop()