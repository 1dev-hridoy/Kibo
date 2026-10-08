import threading
import time
import tkinter as tk

from agent.desktop_widget.config import load_config, save_config
from agent.desktop_widget.api import KiboAPI
from agent.desktop_widget.space_bg import SpaceBackground
from agent.desktop_widget.avatar import MochiAvatar
from agent.desktop_widget.canvas_text import CanvasText


class KiboWidget:
    def __init__(self):
        self.cfg = load_config()
        self.api = KiboAPI(self.cfg["api_base"])
        self.running = True
        self._expanded = False
        self._last_state = None
        self._last_pet_seq = 0
        self._collapse_after = None
        self._last_seen_state = "idle"
        self._peek_until = 0
        self._peek_layout = False
        self._drag_x = None
        self._drag_y = None
        self._idle_seconds = 0
        self._setup_window()
        self._setup_ui()
        self._start_poller()
        self.avatar.wave()

    def _setup_window(self):
        self.root = tk.Tk()
        self.root.title("Kibo")
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.attributes("-alpha", self.cfg["opacity"])
        try:
            self.root.attributes("-type", "dock")
        except Exception:
            pass

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

    def _pet_at(self, event):
        try:
            return self.avatar.hover_at(event.x, event.y)
        except Exception:
            return False

    def _start_drag(self, event):
        if self._pet_at(event):
            self.avatar.click_at(event.x, event.y)
            self._drag_x = None
            self._drag_y = None
            return
        self._drag_x = event.x
        self._drag_y = event.y

    def _on_motion(self, event):
        if self._pet_at(event):
            return
        if self._last_seen_state == "idle" and not self._expanded:
            self._peek_until = time.time() + 2.5
            self._set_expanded(True)
            self.status_label.set_animated("hi!")

    def _do_drag(self, event):
        if self._drag_x is None:
            return
        x = self.root.winfo_x() + event.x - self._drag_x
        y = self.root.winfo_y() + event.y - self._drag_y
        self.root.geometry(f"+{x}+{y}")
        self._last_drag = time.time()

    def _recenter(self):
        if time.time() - getattr(self, "_last_drag", 0) < 5:
            return
        sw = self.root.winfo_screenwidth()
        w = self.root.winfo_width()
        if w < 10:
            return
        cx = (sw - w) // 2
        if abs(self.root.winfo_x() - cx) > 2:
            self.root.geometry(f"+{cx}+{self.cfg.get('y', 0)}")

    def _setup_ui(self):
        bg = self.cfg["bg_color"]
        fg = self.cfg["fg_color"]
        fs = self.cfg["font_size"]

        self.frame = SpaceBackground(self.root, base_color=bg, bg=bg)
        self.frame.pack(fill="both", expand=True)

        avatar_size = self.cfg.get("avatar_size", 100)
        self.avatar = MochiAvatar(self.root, size=avatar_size,
                                  base_bg=bg)
        self.frame.pet = self.avatar
        self.frame.bind("<Motion>", self._on_motion)
        self.frame.bind("<Leave>", lambda e: self.avatar.hover_at(-1, -1))

        self.status_label = CanvasText(self.root, self.frame, 0, fg,
                                       ("Segoe UI", fs + 1, "bold"), 0.38)
        self.task_label = CanvasText(self.root, self.frame, 1, "#9399b2",
                                     ("Segoe UI", fs - 1), 0.62)
        self.tool_label = CanvasText(
            self.root, self.frame, 2,
            self.cfg.get("tool_color", "#94e2d5"),
            ("Consolas", fs - 2), 0.82)
        self.model_label = CanvasText(self.root, self.frame, 3,
                                      self.cfg.get("accent_color", "#89b4fa"),
                                      ("Segoe UI", fs - 1, "bold"), 0,
                                      east=True)

    def _set_expanded(self, expanded: bool):
        if expanded == self._expanded and not self._peek_layout:
            return
        self._expanded = expanded
        h = self.cfg["height"]
        if expanded:
            if time.time() < self._peek_until:
                w = 480
                self._peek_layout = True
            else:
                w = self._w_active
                self._peek_layout = False
            self.avatar.docked_left = True
            x = (self.root.winfo_screenwidth() - w) // 2
            self.root.geometry(f"{w}x{h}+{x}+{self.cfg.get('y', 0)}")
        else:
            w = self._w_idle
            self._peek_layout = False
            self.avatar.docked_left = False
            self.status_label.hide()
            self.task_label.hide()
            self.tool_label.hide()
            self.model_label.hide()
            x = (self.root.winfo_screenwidth() - w) // 2
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
            self.root.after(0, lambda n=name: self.model_label.config(
                text=f" {n} "))
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
                fmsg, fanim, fexp = read_pet_message_file()
                if fmsg:
                    status["custom_message"] = fmsg
                    status["custom_animation"] = fanim
                    status["custom_expires_in"] = fexp
        except Exception:
            pass
        self.root.after(0, lambda: self._apply_status(status))

    def _apply_status(self, status):
        self._recenter()
        state = status.get("state", "idle")
        task = status.get("current_task", "")
        tool = status.get("current_tool", "")
        done = status.get("tools_done", 0)
        total = status.get("tools_total", 0)
        history = status.get("history", [])
        custom = status.get("custom_message", "")
        custom_anim = status.get("custom_animation", "fade")
        custom_exp = status.get("custom_expires_in", 0) or 0
        pet_action = status.get("pet_action", "")
        pet_seq = status.get("pet_seq", 0)
        if pet_seq != self._last_pet_seq:
            self._last_pet_seq = pet_seq
            self.avatar.trigger(pet_action)

        idle_since = status.get("_idle_since", 0)
        recently_active = state != "idle" or (time.time() - idle_since) < 3.0
        peeking = time.time() < self._peek_until
        is_active = state != "idle" or bool(custom) or recently_active or peeking

        if state == "idle" and not custom and not recently_active:
            self._idle_seconds += self.cfg["poll_interval"]
        else:
            self._idle_seconds = 0

        screensaver_sec = self.cfg.get("pixel_screensaver_seconds", 0)
        if screensaver_sec > 0 and self._idle_seconds >= screensaver_sec \
                and state == "idle":
            self.avatar.set_mode("pixel")
            self.frame.set_state_tint("pixel")
        else:
            self.avatar.set_mode("mochi")
            self.frame.set_state_tint(state)

        if state == "idle" and recently_active and \
           self._last_state in ("working", "custom"):
            self.avatar.celebrate()

        self._set_expanded(is_active)

        if state == "idle" and not custom and not recently_active:
            self.avatar.set_state("sleepy" if self._idle_seconds > 20 else "idle")
            if time.time() < self._peek_until:
                self._schedule_collapse(
                    int((self._peek_until - time.time()) * 1000))
            self._last_state = "idle"
            self._last_seen_state = "idle"
            return

        if state == "idle" and not custom and recently_active:
            self.avatar.set_state("idle")
            if self._last_state != "idle" and not self.avatar._confetti:
                self.status_label.set_animated("Done!")
                if history:
                    self.tool_label.set_animated(f"✓ {history[-1]}", delay_ms=100)
                else:
                    self.task_label.set_animated("Task completed", delay_ms=100)
                self._schedule_collapse(5000)
                try:
                    from agent.runner.reminder_sounds import play_sound
                    play_sound("stretch")
                except Exception:
                    pass
            self._last_state = "idle"
            self._last_seen_state = "idle"
            return

        if custom and state == "idle":
            self.avatar.set_state("working")
            if self._last_state != "custom" or \
                    getattr(self, "_shown_custom", "") != custom:
                self._shown_custom = custom
                self.status_label.set_animated(custom, mode=custom_anim)
                self.task_label.hide()
                self.tool_label.hide()
                self._cancel_collapse()
                if custom_exp > 0:
                    self.root.after(custom_exp * 1000,
                                    lambda c=custom: self._expire_custom(c))
            else:
                self.status_label.config(text=custom)
            self._last_state = "custom"
            self._last_seen_state = "idle"
            return

        self.avatar.set_state(state)
        self._cancel_collapse()

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
        self._last_seen_state = state

    def _cancel_collapse(self):
        if self._collapse_after:
            try:
                self.root.after_cancel(self._collapse_after)
            except Exception:
                pass
            self._collapse_after = None

    def _schedule_collapse(self, ms):
        self._cancel_collapse()
        self._collapse_after = self.root.after(ms, self._collapse)

    def _collapse(self):
        self._collapse_after = None
        self.status_label.hide()
        self.task_label.hide()
        self.tool_label.hide()
        self._set_expanded(False)

    def _expire_custom(self, msg=None):
        if msg is not None and msg != getattr(self, "_shown_custom", ""):
            return
        if self._last_seen_state != "idle":
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
        self._collapse()


        

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
        from agent.desktop_widget.settings_dialog import open_settings
        open_settings(self)

    def _quit(self):
        self.running = False
        self.root.destroy()

    def run(self):
        self.root.mainloop()