import math
import random
import tkinter as tk

from agent.desktop_widget.pixel_cat import draw_pixel_cat


class MochiAvatar(tk.Canvas):

    INK = "#2b2438"

    def __init__(self, parent, size=100, base_bg=None, **kwargs):
        super().__init__(parent, width=size, height=size,
                         highlightthickness=0, **kwargs)
        self.size = size
        self.base_bg = base_bg or "#0a0a18"
        self.mode = "mochi"
        self.state = "idle"
        self._base_state = "idle"
        self._frame = random.randint(0, 20)
        self._blink_timer = random.randint(0, 40)
        self._blinking = False
        self._sleep_z = 0
        self._mouse_x = size // 2
        self._mouse_y = size // 2
        self._hovering = False
        self._petted = 0
        self._hearts = []
        self._confetti = []
        self._fx = {"sparkles": [], "fire": [], "bangs": [],
                    "drops": [], "notes": [],
                    "orbit": 0, "rain": 0, "music": 0,
                    "rainbow": 0, "giggle": 0, "zoom": 0, "talk": 0}
        self._yawn_timer = 0
        self._yawning = False
        self._wave_timer = 30
        self.colors = {
            "idle":     "#a6e3a1",
            "working":  "#f9e2af",
            "approval": "#f38ba8",
            "happy":    "#f5c2e7",
            "sleepy":   "#94e2d5",
        }
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Motion>", self._on_motion)
        self.bind("<Button-1>", self._on_click)
        self._animate()



    def set_state(self, state):
        self._base_state = state
        if self._petted == 0:
            self.state = state

    def set_mode(self, mode):
        if mode != self.mode:
            self.mode = mode
            self._yawn_timer = 0
            self._yawning = False

    _FX_ALIASES = [
        ("fireworks", ("fireworks", "firework", "boom", "cracker", "blast")),
        ("sleepy", ("sleepy", "sleep", "yawn", "tired", "nap", "bedtime")),
        ("rainbow", ("rainbow", "rainbow arc", "pride", "colors")),
        ("heartrain", ("heartrain", "heart rain", "hearts rain", "falling hearts", "rain", "shower")),
        ("orbit", ("orbit", "satellite", "halo", "circle", "ring around")),
        ("music", ("music", "sing", "song", "melody", "tune", "humming")),
        ("sparkle", ("sparkle", "sparkles", "shiny", "twinkle", "glitter", "stars")),
        ("giggle", ("giggle", "teehee", "laugh", "haha", "funny")),
        ("zoomies", ("zoomies", "zoom", "run", "dash", "sprint", "fast")),
        ("celebrate", ("celebrate", "dance", "party", "congrats", "yay", "hooray", "clap")),
        ("love", ("love", "hearts", "heart", "pet", "pat", "cuddle", "hug", "kiss")),
        ("happy", ("happy", "joy", "smile", "glad", "cheer")),
        ("sleepy", ("sleepy", "sleep", "yawn", "tired", "nap", "bedtime")),
        ("working", ("working", "busy", "think", "focus")),
        ("talk", ("talk", "talking", "speak", "speaking", "chat",
                 "chatting", "saying")),
        ("pixel", ("pixel", "pixel cat")),
        ("mochi", ("mochi", "normal", "reset")),
    ]



    def trigger(self, action):
        from agent.desktop_widget.pet_anim import start_fx
        a = (action or "").lower()
        kind = None
        for canon, words in self._FX_ALIASES:
            if any(w in a for w in words):
                kind = canon
                break
        if kind is None:
            return
        if kind in ("sparkle", "fireworks", "orbit", "heartrain",
                    "music", "rainbow", "giggle"):
            self._petted = 120
            self.state = "happy"
            fx = "heartrain" if kind == "heartrain" else kind
            start_fx(self, fx)
            return
        if kind == "zoomies":
            self._petted = 100
            self.state = "working"
            start_fx(self, "zoomies")
            return
        if kind == "talk":
            import re as _re
            m = _re.search(r"(\d+)", a)
            frames = int(m.group(1)) if m else 120
            self._petted = max(self._petted, min(400, frames))
            self.state = "happy"
            start_fx(self, f"talk:{frames}")
            return
        if kind == "celebrate":
            self.celebrate()
            self._petted = 60
        elif kind == "love":
            self._petted = 60
            self.state = "happy"
            for _ in range(5):
                self._hearts.append({
                    "x": random.uniform(10, self.size - 10),
                    "y": random.uniform(4, self.size * 0.4),
                    "life": random.randint(20, 35),
                })

                
        elif kind == "happy":
            self._petted = 90
            self.state = "happy"
        elif kind == "sleepy":
            self._petted = 90
            self.state = "sleepy"
        elif kind == "working":
            self._petted = 90
            self.state = "working"
        elif kind == "pixel":
            self.set_mode("pixel")
        elif kind == "mochi":
            self.set_mode("mochi")
            self.state = "idle"

    def celebrate(self):
        self._petted = 30
        self.state = "happy"
        for _ in range(18):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(2, 5)
            self._confetti.append({
                'x': self.size // 2,
                'y': self.size // 2,
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed - 1.5,
                'life': 60,
                'color': random.choice(("#f9e2af", "#f5c2e7", "#89dceb",
                                        "#a6e3a1", "#cba6f7", "#f38ba8")),
                'size': random.uniform(3, 6),
            })





    def _on_enter(self, e):
        self._hovering = True

    def _on_leave(self, e):
        self._hovering = False
        self._mouse_x = self.size // 2
        self._mouse_y = self.size // 2

    def _on_motion(self, e):
        self._mouse_x = e.x
        self._mouse_y = e.y

    def _on_click(self, e):
        self._petted = 45
        self.state = "happy"
        for _ in range(6):
            self._hearts.append({
                'x': self.size // 2 + random.uniform(-6, 6),
                'y': self.size // 2 + random.uniform(-4, 2),
                'vx': random.uniform(-1.5, 1.5),
                'vy': random.uniform(-2.5, -1.0),
                'life': 45,
                'size': random.uniform(8, 12),
            })
        return "break"





    def _animate(self):
        self._frame += 1
        self._blink_timer += 1
        blink_period = 30 if self._hovering else 70
        if self._blink_timer > blink_period:
            self._blinking = True
            self._blink_timer = 0
        if self._blinking and self._blink_timer > 4:
            self._blinking = False
        if self.state == "idle" and self._frame % 60 == 0:
            self._sleep_z = (self._sleep_z + 1) % 4
        elif self.state != "idle":
            self._sleep_z = 0
        if self.state == "idle" and self._yawn_timer > 0:
            self._yawn_timer -= 1
            self._yawning = self._yawn_timer > 30
        elif self.state == "idle" and self._frame % 400 == 0:
            self._yawn_timer = 50
        if self._wave_timer > 0:
            self._wave_timer -= 1
        if self._petted > 0:
            self._petted -= 1
            if self._petted == 0:
                self.state = self._base_state
        for h in self._hearts:
            h['x'] += h['vx']
            h['y'] += h['vy']
            h['vy'] += 0.05
            h['life'] -= 1
        self._hearts = [h for h in self._hearts if h['life'] > 0]
        for c in self._confetti:
            c['x'] += c['vx']
            c['y'] += c['vy']
            c['vy'] += 0.12
            c['vx'] *= 0.99
            c['life'] -= 1
        self._confetti = [c for c in self._confetti if c['life'] > 0]
        from agent.desktop_widget.pet_anim import update_fx
        update_fx(self)
        self._draw()
        self.after(50, self._animate)





    def _draw(self):
        if self.mode == "pixel":
            draw_pixel_cat(self, self.size, self._frame, self._blinking)
        else:
            self._draw_mochi()
        from agent.desktop_widget.pet_anim import draw_fx
        draw_fx(self)

    def _draw_mochi(self):
        from agent.desktop_widget.mochi_draw import draw_mochi
        draw_mochi(self)