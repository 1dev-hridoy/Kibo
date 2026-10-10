import threading
import time
import tkinter as tk

from agent.desktop_widget.config import load_config, save_config
from agent.desktop_widget.api import KiboAPI
from agent.desktop_widget.space_bg import SpaceBackground
from agent.desktop_widget.avatar import MochiAvatar
from agent.desktop_widget.canvas_text import CanvasText

class KiboWidget:
    MEDIA_ANIMS = {
        "youtube": ["ytwave", "ytplay", "ytbars"],
        "spotify": ["spnote", "spbars", "spwave"],
        "other": ["music"],
    }
    MEDIA_ROTATE_SEC = 3.4

    def __init__(self):
        self.cfg = load_config()
        self.api = KiboAPI(self.cfg["api_base"])
        self.running = True
        self._expanded = False
        self._last_state = None
        self._last_pet_seq = 0
        self._media_tint = None
        self._media_key = None
        self._media_anim_idx = 0
        self._media_anim_at = 0.0
        self._poll_warned = False
        self._collapse_after = None
        self._last_seen_state = "idle"
        self._peek_until = 0
        self._hovering = False
        self._shown_custom = ""
        self._cur_custom = ""
        self._cur_anim = "fade"
        self._card_hidden = False
        self._card_key = None
        self._msg_collapsed = False
        self._msg_timer_armed = False
        self._msg_mtime = None
        self._scroll_active = False
        self._scroll_seq = 0
        self._pending_scroll = None
        self._scroll_msgs = []
        self._scroll_idx = 0
        self._scroll_t = 0.0
        self._scroll_last = ""
        self._compact = False
        self._drag_x = None
        self._drag_y = None
        self._idle_seconds = 0
        self._setup_window()
        self._setup_ui()
        self._start_poller()
        self.avatar.wave()
        self._model_name = ""
        self._loading_token = 0
        self._set_expanded(True, compact=True)
        self.status_label.config(text="Loading model…")

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
        from agent.desktop_widget.pointer import start_drag
        self.root.bind("<Button-1>", lambda e: start_drag(self, e))
        self.root.bind("<B1-Motion>", self._do_drag)

    def _do_drag(self, event):
        if self._drag_x is None:
            return
        x = self.root.winfo_x() + event.x - self._drag_x
        y = self.root.winfo_y() + event.y - self._drag_y
        self.root.geometry(f"+{x}+{y}")
        self._last_drag = time.time()

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
        from agent.desktop_widget.pointer import on_motion, on_leave
        self.frame.bind("<Motion>", lambda e: on_motion(self, e))
        self.frame.bind("<Leave>", lambda e: on_leave(self, e))

        self._font_status = ("Segoe UI", fs + 1, "bold")
        self._font_info = ("Segoe UI", fs - 1)
        self.status_label = CanvasText(self.root, self.frame, 0, fg,
                                       self._font_status, 0.38)
        self.task_label = CanvasText(self.root, self.frame, 1, "#9399b2",
                                     self._font_info, 0.62)
        self.tool_label = CanvasText(
            self.root, self.frame, 2,
            self.cfg.get("tool_color", "#94e2d5"),
            ("Consolas", fs - 2), 0.82)
        self.model_label = CanvasText(self.root, self.frame, 3,
                                      self.cfg.get("accent_color", "#89b4fa"),
                                      ("Segoe UI", fs - 1, "bold"), 0,
                                      east=True)

    def _set_expanded(self, expanded: bool, compact: bool = False):
        if expanded == self._expanded and compact == self._compact:
            return
        self._expanded = expanded
        self._compact = compact
        h = self.cfg["height"]
        if expanded:
            w = 480 if compact else self._w_active
            self.avatar.docked_left = True
        else:
            w = self._w_idle
            self.avatar.docked_left = False
            self._card_hidden = True
            self.status_label.hide()
            self.task_label.hide()
            self.tool_label.hide()
            self.model_label.hide()
        from agent.desktop_widget.window_fx import animate_width
        for lbl in (self.status_label, self.task_label, self.tool_label):
            lbl.set_wrap(max(140, w - 150))
        animate_width(self, w)

    def _start_poller(self):
        def poll():
            while self.running:
                try:
                    self._fetch_status()
                except Exception as e:


                    if not self._poll_warned:
                        self._poll_warned = True
                        print(f"[Widget] poll error: {e}")
                time.sleep(self.cfg["poll_interval"])
        threading.Thread(target=poll, daemon=True).start()

    def _fetch_status(self):
        model_info = self.api.get_model()
        if "active" in model_info:
            name = model_info.get("name", model_info["active"])
            if name != self._model_name:
                first = not self._model_name
                self._model_name = name
                if first:
                    self.avatar.loading = False
                else:
                    self.avatar.loading = True
                    self.root.after(0, lambda n=name: self.status_label.config(
                        text=f"Loading {n}…"))
                    self._loading_token += 1
                    tok = self._loading_token
                    self.root.after(30000, lambda: self._loading_done(tok))
            self.root.after(0, lambda n=name: self.model_label.config(
                text=f" {n} "))
        else:
            # No model info (server down or not started yet) - stop the
            # startup spinner so the idle card is not blocked forever.
            self.avatar.loading = False
        status = self.api.get_status()
        if "error" in status:
            status = {"state": "idle", "current_task": "", "current_tool": "",
                      "tools_done": 0, "tools_total": 0, "history": [],
                      "custom_message": "", "_idle_since": 0}

        from agent.desktop_widget.msg_state import merge_shared_files
        merge_shared_files(self, status)
        self.root.after(0, lambda: self._apply_status(status))

    def _apply_status(self, status):
        from agent.desktop_widget.window_fx import recenter
        recenter(self)
        state = status.get("state", "idle")
        task = status.get("current_task", "")
        tool = status.get("current_tool", "")
        done = status.get("tools_done", 0)
        total = status.get("tools_total", 0)
        history = status.get("history", [])
        custom = status.get("custom_message", "")
        custom_anim = status.get("custom_animation", "fade")
        custom_exp = status.get("custom_expires_in", 0) or 0
        self._cur_custom = custom
        self._cur_anim = custom_anim
        pet_action = status.get("pet_action", "")
        pet_seq = status.get("pet_seq", 0)
        if pet_seq != self._last_pet_seq:
            self._last_pet_seq = pet_seq
            self.avatar.trigger(pet_action)

        media = status.get("media") or {}
        self._apply_media(media)

        idle_since = status.get("_idle_since", 0)
        recently_active = state != "idle" or (time.time() - idle_since) < 3.0
        if state == "idle" and not custom and not recently_active:
            self._idle_seconds += self.cfg["poll_interval"]
        else:
            self._idle_seconds = 0

        screensaver_sec = self.cfg.get("pixel_screensaver_seconds", 0)
        if screensaver_sec > 0 and self._idle_seconds >= screensaver_sec \
                and state == "idle":
            self.avatar.set_mode("pixel")
            self.frame.set_state_tint("pixel")
        elif self._media_tint is not None and state == "idle":
            self.avatar.set_mode("mochi")
            self.frame.set_state_tint(self._media_tint)
        else:
            self.avatar.set_mode("mochi")
            self.frame.set_state_tint(state)

        if state == "idle" and recently_active and \
           self._last_state in ("working", "custom"):
            self.avatar.celebrate()

        if self._pending_scroll:
            msgs = self._pending_scroll
            self._pending_scroll = None
            from agent.desktop_widget.scroll_player import start
            start(self, msgs)


        if self._scroll_active:
            self._last_state = "custom"
            self._last_seen_state = "idle"
            return

        peeking = self._hovering or time.time() < self._peek_until
        if custom and self._msg_collapsed:
            # message already auto-collapsed: only a real hover reopens it
            is_active = self._hovering
        else:
            is_active = state != "idle" or bool(custom) or recently_active \
                or peeking
        self._set_expanded(is_active, compact=(state == "idle"))

        if state == "idle" and not custom and not recently_active:
            self.avatar.set_state("sleepy" if self._idle_seconds > 20 else "idle")
     
     
            if peeking and not self.avatar.loading:
                self._render_idle_card()
                if self._hovering:
                    self._cancel_collapse()
                else:
                    self._schedule_collapse(
                        int((self._peek_until - time.time()) * 1000))
            else:
                self._card_hidden = True
                self.status_label.hide()
                self.task_label.hide()
                self.tool_label.hide()
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
            self.avatar.set_state("idle")
            changed = getattr(self, "_shown_raw", "") != custom
            if changed or self._last_state != "custom":
                self._msg_collapsed = False
                self._msg_timer_armed = False



            elif self._msg_collapsed and self._hovering:
                # pointing at a collapsed widget brings the message back
                self._msg_collapsed = False
                self._msg_timer_armed = False


            if self._msg_collapsed:
                self._card_hidden = True
                self.status_label.hide()
                self.task_label.hide()
                self.tool_label.hide()
            else:
                self._render_idle_card(custom, custom_anim, animate=changed)
                if changed or self._last_state != "custom":
                    self.avatar.trigger("sparkle")

                    
                    if custom_exp > 0:
                        self.root.after(
                            custom_exp * 1000,
                            lambda c=custom: self._expire_custom(c))
                if not self._msg_timer_armed:
                    self._cancel_collapse()
                    self._schedule_collapse(5000)
                    self._msg_timer_armed = True
            self._last_state = "custom"
            self._last_seen_state = "idle"
            return

        self.avatar.set_state(state)
        self._cancel_collapse()

        from agent.desktop_widget.task_card import render_task_card
        render_task_card(self, state, task, custom, tool,
                         done, total, history)

        self._last_state = state
        self._last_seen_state = state

    def _apply_media(self, media):
        playing = bool(media and media.get("playing"))



        if not playing:
            if self._media_tint is not None:
                self._media_tint = None
                self._media_key = None
                self._media_anim_idx = 0
                self._media_anim_at = 0.0
                for k in ("ytwave", "ytplay", "ytbars",
                          "spwave", "spbars", "spnote",
                          "music", "newtrack"):
                    self.avatar._fx[k] = 0
                self.avatar._fx["notes"].clear()
                self.avatar.trigger("mochi")
            return
        




        source = (media or {}).get("source", "other")
        key = (media or {}).get("track_key", "")




        if self._media_tint != source:

            self._media_tint = source
            self.frame.set_state_tint(source)

        anims = self.MEDIA_ANIMS.get(source, self.MEDIA_ANIMS["other"])
        now = time.time()

        if key and key != self._media_key:
            self._media_key = key
            self._media_anim_idx = 0
            self.avatar.trigger("newtrack")
            self._media_anim_at = now

            
        elif now - self._media_anim_at >= self.MEDIA_ROTATE_SEC:
            self.avatar.trigger(anims[self._media_anim_idx % len(anims)])
            self._media_anim_idx += 1
            self._media_anim_at = now

    def _sys_info(self):
        from agent.desktop_widget.sys_info import sys_info
        return sys_info()

    def _loading_done(self, tok):
        if tok == self._loading_token:
            self.avatar.loading = False

    def _cancel_collapse(self):
        from agent.desktop_widget.msg_state import cancel_collapse
        cancel_collapse(self)

    def _schedule_collapse(self, ms):
        from agent.desktop_widget.msg_state import schedule_collapse
        schedule_collapse(self, ms)

    def _render_idle_card(self, custom="", anim="fade", animate=None):
        from agent.desktop_widget.idle_card import render_idle_card
        render_idle_card(self, custom, anim, animate)

    def _collapse(self):
        from agent.desktop_widget.msg_state import collapse
        collapse(self)

    def _expire_custom(self, msg=None):
        from agent.desktop_widget.msg_state import expire_custom
        expire_custom(self, msg)

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
