import math
import random

from agent.desktop_widget.pixel_cat import draw_pixel_cat


class _PetView:
    def __init__(self, cv, dx, dy, state):
        self._cv = cv
        self._dx = dx
        self._dy = dy
        self._state = state



    def __getattr__(self, name):
        return getattr(self._state, name)


    def delete(self, *args):
        self._cv.delete("pet")




    def _shift(self, args):
        out = []
        for i, v in enumerate(args):
            if isinstance(v, (int, float)):
                v = v + (self._dx if i % 2 == 0 else self._dy)
            out.append(v)
        return out




    def _tag(self, kw):
        tags = kw.pop("tags", None)
        if isinstance(tags, (list, tuple)):
            kw["tags"] = ("pet",) + tuple(tags)


        elif tags:
            kw["tags"] = ("pet", tags)


        else:

            kw["tags"] = ("pet",)

    def create_oval(self, *args, **kw):
        self._tag(kw)
        return self._cv.create_oval(*self._shift(args), **kw)



    def create_rectangle(self, *args, **kw):
        self._tag(kw)
        return self._cv.create_rectangle(*self._shift(args), **kw)



    def create_line(self, *args, **kw):
        self._tag(kw)
        return self._cv.create_line(*self._shift(args), **kw)



    def create_polygon(self, *args, **kw):
        self._tag(kw)
        return self._cv.create_polygon(*self._shift(args), **kw)



    def create_arc(self, *args, **kw):
        self._tag(kw)
        return self._cv.create_arc(*self._shift(args), **kw)

    def create_text(self, *args, **kw):
        self._tag(kw)
        return self._cv.create_text(*self._shift(args), **kw)



class MochiAvatar:

    INK = "#2b2438"

    def __init__(self, root, size=100, base_bg=None):
        self.root = root
        self.size = size
        self.base_bg = base_bg or "#0a0a18"
        self.mode = "mochi"
        self.state = "idle"
        self.docked_left = False
        self.x0 = 0
        self.y0 = 0
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
                    "drops": [], "notes": [], "wdrops": [],
                    "orbit": 0, "rain": 0, "music": 0,
                    "newtrack": 0,
                    "ytwave": 0, "ytplay": 0, "ytbars": 0,
                    "spwave": 0, "spbars": 0, "spnote": 0,
                    "flip": 0, "flip_dir": 1,
                    "coinflip": 0, "coin_face": "heads",
                    "coin_spin": 0, "coin_spark": False,
                    "rainbow": 0, "giggle": 0, "zoom": 0, "talk": 0,
                    "water": 0, "grass": 0, "stretch": 0,
                    "eyes": 0, "posture": 0}
        self._yawn_timer = 0
        self._yawning = False
        self._wave_timer = 30
        self._squish = 0.0
        self._dizzy = 0
        self._clicks = []
        self._showcase = []
        self._idle_anim_in = 300
        self.loading = True
        self.colors = {
            "idle":     "#a6e3a1",
            "working":  "#f9e2af",
            "approval": "#f38ba8",
            "happy":    "#f5c2e7",
            "sleepy":   "#94e2d5",
            "annoyed":  "#fab387",
            "dizzy":    "#cba6f7",
        }
        self._tick()



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
        ("ytwave", ("ytwave", "youtube wave", "red wave")),
        ("ytplay", ("ytplay", "play button", "watch")),
        ("ytbars", ("ytbars", "youtube bars", "red bars")),
        ("spnote", ("spnote", "spotify notes", "green notes")),
        ("spbars", ("spbars", "spotify bars", "green bars")),
        ("spwave", ("spwave", "spotify rings", "green rings")),
        ("coinflip", ("coinflip", "coin flip", "flip a coin",
                      "toss a coin", "heads or tails", "coin")),
        ("flip", ("flip", "flip the pet", "backflip", "frontflip",
                  "somersault", "tumble", "airflip", "spin me")),

        ("newtrack", ("newtrack", "new track", "new song",
                      "track changed", "now playing")),
        ("sparkle", ("sparkle", "sparkles", "shiny", "twinkle", "glitter", "stars")),
        ("giggle", ("giggle", "teehee", "laugh", "haha", "funny")),
        ("zoomies", ("zoomies", "zoom", "run", "dash", "sprint", "fast")),
        ("celebrate", ("celebrate", "dance", "party", "congrats", "yay", "hooray", "clap")),
        ("love", ("love", "hearts", "heart", "pet", "pat", "cuddle", "hug", "kiss")),
        ("happy", ("happy", "joy", "smile", "glad", "cheer")),
        ("annoyed", ("annoyed", "annoy", "grumpy", "poke", "poked")),
        ("dizzy", ("dizzy", "dazed", "spin head", "confused")),
        ("sleepy", ("sleepy", "sleep", "yawn", "tired", "nap", "bedtime")),
        ("working", ("working", "busy", "think", "focus")),
        ("talk", ("talk", "talking", "speak", "speaking", "chat",
                 "chatting", "saying")),


        ("showcase", ("showcase", "parade", "play all", "show all",
                      "all animations", "marathon", "demo", "everything")),
        ("water", ("water", "drink", "hydrate", "thirsty", "glass of water")),
        ("grass", ("grass", "touch grass", "outside", "nature", "park",
                  "fresh air", "go outside")),
        ("stretch", ("stretch", "stretching", "yoga", "stand up", "move")),
        ("eyes", ("eyes", "eye", "blink", "20-20-20", "look far",
                 "eye break", "rest eyes")),
        ("posture", ("posture", "sit", "straight", "spine",
                    "sit tall", "shoulders")),
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
                    "music", "newtrack",
                    "ytwave", "ytplay", "ytbars",
                    "spwave", "spbars", "spnote",
                    "flip", "coinflip",
                    "rainbow", "giggle"):
            self._petted = 120
            self.state = "happy"
            fx = "heartrain" if kind == "heartrain" else kind
            start_fx(self, fx)
            return
        if kind in ("water", "grass", "stretch", "eyes", "posture"):
            self._petted = 150
            self.state = "happy"
            start_fx(self, kind)
            return
        if kind == "annoyed":
            self._squish = 1.0
            self._petted = 70
            self.state = "annoyed"
            return
        if kind == "dizzy":
            self._dizzy = 110
            self._petted = max(self._petted, 110)
            self.state = "dizzy"
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
        if kind == "showcase":
            self._showcase = ["sparkle", "music", "giggle", "orbit",
                              "rainbow", "fireworks", "heartrain",
                              "zoomies", "dance", "love", "happy",
                              "stretch", "water", "grass", "sleepy",
                              "flip", "coinflip"]
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
                    "vx": random.uniform(-1, 1),
                    "vy": random.uniform(-2, -1),
                    "life": random.randint(20, 35),
                    "size": random.uniform(8, 12),
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

    def hover_at(self, x, y):
        s = self.size
        inside = self.x0 <= x <= self.x0 + s and self.y0 <= y <= self.y0 + s
        self._hovering = inside

        if inside:
            self._mouse_x = x - self.x0
            self._mouse_y = y - self.y0


        else:
            self._mouse_x = s // 2
            self._mouse_y = s // 2
        return inside



    def click_at(self, x, y):
        s = self.size
        if self.x0 <= x <= self.x0 + s and self.y0 <= y <= self.y0 + s:
            import time as _t
            now = _t.time()
            self._clicks = [c for c in self._clicks if now - c < 1.2]
            self._clicks.append(now)
            self._squish = 1.0

            if len(self._clicks) >= 3:
                self._clicks = []
                self._dizzy = 110
                self._petted = max(self._petted, 110)
                self.state = "dizzy"
                try:
                    from agent.core.agent_state import set_widget_message
                    set_widget_message(
                        "Too many hits at once. "
                        "Give me a sec.", "fade", expires_in=3)
                except Exception:
                    pass


            else:
                self._petted = max(self._petted, 50)
                self.state = "annoyed"
            return True
        return False

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





    def wave(self):
        self._wave_timer = 110

    def _tick(self):
        self._animate()
        self.root.after(50, self._tick)

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
        if self._squish > 0.02:
            self._squish *= 0.90
        else:
            self._squish = 0.0
        if self._dizzy > 0:
            self._dizzy -= 1
            if self._dizzy == 0 and self._petted == 0:
                self.state = self._base_state
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
        self._auto_play()

    def _fx_busy(self):
        fx = self._fx
        if fx["sparkles"] or fx["fire"] or fx["drops"] or fx["notes"] \
                or fx["wdrops"] or fx["bangs"]:
            return True
        return any(fx.get(k, 0) > 0 for k in
                   ("orbit", "rain", "music", "newtrack",
                    "ytwave", "ytplay", "ytbars",
                    "spwave", "spbars", "spnote",
                    "flip", "coinflip",
                    "rainbow", "giggle", "zoom",
                    "talk", "water", "grass", "stretch", "eyes", "posture"))



    def _auto_play(self):
        if self._showcase:
            if self._petted == 0 and not self._fx_busy():
                self.trigger(self._showcase.pop(0))
            return


    def draw(self, cv):
        w = cv.winfo_width()
        h = cv.winfo_height()
        s = self.size
        if self.docked_left:
            self.x0 = 18
        else:
            self.x0 = max(0, (w - s) // 2)
        self.y0 = max(0, (h - s) // 2)
        view = _PetView(cv, self.x0, self.y0, self)
        if self.mode == "pixel":
            draw_pixel_cat(view, self.size, self._frame, self._blinking)
        else:
            from agent.desktop_widget.mochi_draw import draw_mochi
            draw_mochi(view)
        from agent.desktop_widget.pet_anim import draw_fx
        draw_fx(view)
        if self.loading:
            rr = s // 2 + 12
            for i in range(8):
                ang = self._frame * 0.15 + i * math.pi / 4
                lit = (i + self._frame // 5) % 8 < 3
                dx = math.cos(ang) * rr
                dy = math.sin(ang) * rr * 0.9
                view.create_oval(s // 2 + dx - 2.5, s // 2 + dy - 2.5,
                                 s // 2 + dx + 2.5, s // 2 + dy + 2.5,
                                 fill="#89dceb" if lit else "#313244",
                                 outline="")
