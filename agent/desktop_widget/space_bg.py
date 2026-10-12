import math
import random
import tkinter as tk


class SpaceBackground(tk.Canvas):
    STATE_TINTS = {
        "idle":     (8, 8, 22),
        "working":  (22, 16, 10),
        "approval": (26, 10, 22),
        "happy":    (22, 14, 28),
        "pixel":    (5, 16, 10),
        "youtube":  (64, 10, 10),
        "spotify":  (29, 185, 84),
        "other":    (10, 12, 28),
    }

    MID_STAR_COLORS = ("#ffffff", "#fff3b0", "#b4befe", "#f5c2e7", "#89dceb")
    NEAR_STAR_COLORS = ("#ffffff", "#fff3b0", "#b4befe")

    LIGHT_STAR_COLORS = ("#9a8fa3", "#a89a8c", "#8f9aae", "#ab94a4", "#93a3b0")
    NEBULA_COLORS = (
        (255, 100, 200),
        (100, 150, 255),
        (200, 100, 255),
        (255, 180, 100),



    )




    

    def __init__(self, parent, base_color="#0a0a18", theme="midnight", **kwargs):
        super().__init__(parent, highlightthickness=0, **kwargs)
        self.base_color = base_color
        self.state_tint = self.STATE_TINTS["idle"]
        self.renderer = "space"
        self.tints = dict(self.STATE_TINTS)
        self.state = "idle"
        self.light_bg = False
        self._frame = 0
        self._seeded = False
        self._last_w = 0
        self._last_h = 0
        self._stars_far = []
        self._stars_mid = []
        self._stars_near = []
        self._nebulae = []
        self._shooting_stars = []
        self._petals = []
        self._glints = []
        self.texts = []
        self.card_w = 0
        self.set_theme(theme)
        self._animate()

    def set_theme(self, theme):
        """Apply a theme dict (or theme key) to the background.

        Re-seeds particles because the palette and density both change.
        """
        from agent.desktop_widget.config import resolve_theme
        _, t = resolve_theme(theme if isinstance(theme, str) else "midnight")


        if isinstance(theme, dict):
            t = theme


        self.tints = dict(t.get("tints", self.STATE_TINTS))
        self.renderer = t.get("background", "space")
        cur = getattr(self, "state", "idle")
        self.set_state_tint(cur)
        self._seeded = False

    def set_state_tint(self, state):
        self.state = state
        self.state_tint = self.tints.get(state, self.tints["idle"])


       
        r, g, b = self.state_tint
        self.light_bg = (0.299 * r + 0.587 * g + 0.114 * b) > 140

    def base_hex(self):
        r, g, b = self.state_tint
        return f"#{r:02x}{g:02x}{b:02x}"







    def _seed_space(self, w, h):
        self._stars_far = [{
            'x': random.uniform(0, w),
            'y': random.uniform(0, h),
            'r': random.uniform(0.4, 0.9),
            'vx': random.uniform(-0.06, -0.02),
            'phase': random.uniform(0, math.pi * 2),
            'bright': random.uniform(0.4, 0.7),
        } for _ in range(90)]
        self._stars_mid = [{
            'x': random.uniform(0, w),
            'y': random.uniform(0, h),
            'r': random.uniform(0.9, 1.4),
            'vx': random.uniform(-0.15, -0.08),
            'phase': random.uniform(0, math.pi * 2),
            'color': random.choice(self.LIGHT_STAR_COLORS
                                   if self.light_bg else self.MID_STAR_COLORS),
        } for _ in range(30)]
        self._stars_near = [{
            'x': random.uniform(0, w),
            'y': random.uniform(5, h - 5),
            'r': random.uniform(1.5, 2.5),
            'vx': random.uniform(-0.30, -0.18),
            'phase': random.uniform(0, math.pi * 2),
            'color': random.choice(self.LIGHT_STAR_COLORS
                                   if self.light_bg else self.NEAR_STAR_COLORS),
        } for _ in range(8)]
        self._nebulae = [{
            'x': random.uniform(50, w - 50),
            'y': random.uniform(15, h - 15),
            'r': random.uniform(30, 55),
            'vx': random.uniform(-0.05, -0.02),
            'color': color,
            'phase': random.uniform(0, math.pi * 2),
        } for color in self.NEBULA_COLORS]

    def _animate(self):
        self._frame += 1
        if random.random() < 0.004:
            w = self.winfo_width() if self.winfo_width() > 1 else 500
            self._shooting_stars.append({
                'x': random.uniform(0, w * 0.5),
                'y': random.uniform(0, 25),
                'vx': random.uniform(4, 7),
                'vy': random.uniform(1.5, 2.5),
                'life': 40,
                'trail': [],
            })
        self._draw()
        self.after(50, self._animate)








    def _draw(self):
        self.delete("all")
        w = self.winfo_width()
        h = self.winfo_height()
        if w < 4 or h < 4:
            return
        if not self._seeded or abs(w - self._last_w) > 40 \
                or abs(h - self._last_h) > 20:
            if self.renderer == "anime":
                self._seed_anime(w, h)
            else:
                self._seed_space(w, h)
            self._seeded = True
            self._last_w, self._last_h = w, h

        if self.renderer == "anime":
            self._draw_anime(w, h)
        else:
            self._draw_space(w, h)
        self._draw_overlay(w, h)



    def _draw_overlay(self, w, h):
        """Pet + text layer, drawn on top of whichever sky is active."""
        pet = getattr(self, "pet", None)
        if pet is not None:
            try:
                pet.draw(self)
            except Exception:



                pass
        for t in self.texts:
            if t.get("text"):
                if t.get("east"):
                    tx, ty = max(0, w - 12), 16
                else:
                    ty = int(h * t.get("row", 0.3)) + int(t.get("dy", 0))
                    tx = 142


                if t.get("shadow", True):

                    self.create_text(tx + 1, ty + 1,
                                     text=t["text"],
                                     anchor=t.get("anchor", "w"),
                                     fill="#000000",
                                     font=t.get("font", ("Segoe UI", 10)))
                kw = {"anchor": t.get("anchor", "w"),
                      "fill": t.get("fill", "#ffffff"),
                      "font": t.get("font", ("Segoe UI", 10))}
                if t.get("wrap"):
                    kw["width"] = t["wrap"]
                self.create_text(tx, ty, text=t["text"], **kw)

    def _draw_space(self, w, h):
        r0, g0, b0 = self.state_tint
        N = 12
        for i in range(N):
            t = i / (N - 1)
            factor = 1.0 + math.sin(t * math.pi) * 0.15
            r = min(255, int(r0 * factor))
            g = min(255, int(g0 * factor))
            b = min(255, int(b0 * factor))
            self.create_rectangle(0, int(i * h / N),
                                  w, int((i + 1) * h / N) + 1,
                                  fill=f"#{r:02x}{g:02x}{b:02x}", outline="")

            





        for n in (() if self.light_bg else self._nebulae):
            n['x'] += n['vx']
            if n['x'] < -n['r']:
                n['x'] = w + n['r']
                n['y'] = random.uniform(10, h - 10)
            pulse = math.sin(self._frame * 0.02 + n['phase']) * 0.3 + 0.7
            r, g, b = n['color']
            for ring in range(5):
                rr = n['r'] * (1 - ring * 0.18) * pulse
                if rr < 1:
                    continue
                stip = "gray12" if ring > 2 else "gray25"
                self.create_oval(n['x'] - rr, n['y'] - rr,
                                 n['x'] + rr, n['y'] + rr,
                                 fill=f"#{r:02x}{g:02x}{b:02x}",
                                 outline="", stipple=stip)



                

        for s in self._stars_far:
            s['x'] += s['vx']
            if s['x'] < -2:
                s['x'] = w + 2
                s['y'] = random.uniform(0, h)
            tw = math.sin(self._frame * 0.04 + s['phase']) * 0.3 + 0.7
            bright = s['bright'] * tw
            stip = "gray50" if bright > 0.5 else "gray25"
            self.create_oval(s['x'] - s['r'], s['y'] - s['r'],
                             s['x'] + s['r'], s['y'] + s['r'],
                             fill="#ffffff", outline="", stipple=stip)

        for s in self._stars_mid:
            s['x'] += s['vx']
            if s['x'] < -2:
                s['x'] = w + 2
                s['y'] = random.uniform(0, h)
            tw = math.sin(self._frame * 0.08 + s['phase']) * 0.4 + 0.6
            stip = "gray50" if tw > 0.5 else "gray25"
            self.create_oval(s['x'] - s['r'], s['y'] - s['r'],
                             s['x'] + s['r'], s['y'] + s['r'],
                             fill=s['color'], outline="", stipple=stip)


            

        for s in self._stars_near:
            s['x'] += s['vx']
            if s['x'] < -3:
                s['x'] = w + 3
                s['y'] = random.uniform(0, h)
            tw = math.sin(self._frame * 0.10 + s['phase']) * 0.3 + 0.7
            flare_len = s['r'] * 5 * tw
            self.create_line(s['x'] - flare_len, s['y'],
                             s['x'] + flare_len, s['y'],
                             fill=s['color'], width=1)
            self.create_line(s['x'], s['y'] - flare_len,
                             s['x'], s['y'] + flare_len,
                             fill=s['color'], width=1)
            d = flare_len * 0.5
            self.create_line(s['x'] - d, s['y'] - d,
                             s['x'] + d, s['y'] + d,
                             fill=s['color'], width=1, stipple="gray50")
            self.create_line(s['x'] - d, s['y'] + d,
                             s['x'] + d, s['y'] - d,
                             fill=s['color'], width=1, stipple="gray50")
            self.create_oval(s['x'] - s['r'], s['y'] - s['r'],
                             s['x'] + s['r'], s['y'] + s['r'],
                             fill=s['color'], outline="")
            self.create_oval(s['x'] - s['r'] * 0.4, s['y'] - s['r'] * 0.4,
                             s['x'] + s['r'] * 0.4, s['y'] + s['r'] * 0.4,
                             fill="#ffffff", outline="")







        for s in self._shooting_stars:
            s['x'] += s['vx']
            s['y'] += s['vy']
            s['life'] -= 1
            s['trail'].append((s['x'], s['y']))
            if len(s['trail']) > 12:
                s['trail'].pop(0)
            for i, (tx, ty) in enumerate(s['trail']):
                t = i / max(1, len(s['trail']))
                size = max(0.5, 2.0 * t)
                stip = "gray50" if t > 0.5 else "gray25"
                self.create_oval(tx - size, ty - size,
                                 tx + size, ty + size,
                                 fill="#ffffff", outline="", stipple=stip)
            self.create_oval(s['x'] - 2, s['y'] - 2, s['x'] + 2, s['y'] + 2,
                             fill="#ffffff", outline="")
        self._shooting_stars = [s for s in self._shooting_stars
                                if s['life'] > 0 and s['x'] < w + 30]






    SKY_TOP = (0.55, 0.30, 0.75)
    SKY_BOTTOM = (0.95, 0.45, 0.62)
    MOON_POS = (0.78, 0.30)
    MOON_R = 26
    PETAL_COLORS = (
        "#ffd7e8", "#ffc2dc", "#ffe9f3", "#ffb3d9",
        "#f7c6e8", "#ffffff",
    )
    GLINT_COLORS = ("#fff6ff", "#ffe0f4", "#d9f4ff", "#fff0a8")

    def _seed_anime(self, w, h):
        n_petals = max(14, min(46, int(w / 14)))
        self._petals = [{
            'x': random.uniform(-20, w + 20),
            'y': random.uniform(-h, h),
            'r': random.uniform(2.8, 6.2),
            'vy': random.uniform(0.18, 0.65),
            'vx': random.uniform(-0.22, 0.22),
            'sway': random.uniform(0.4, 1.3),
            'sway_phase': random.uniform(0, math.pi * 2),
            'sway_rate': random.uniform(0.04, 0.09),
            'spin': random.uniform(-0.06, 0.06),
            'rot': random.uniform(0, math.pi * 2),
            'color': random.choice(self.PETAL_COLORS),
            'alpha': random.uniform(0.45, 1.0),
        } for _ in range(n_petals)]



        self._glints = [{
            'x': random.uniform(0, w),
            'y': random.uniform(0, h * 0.85),
            'r': random.uniform(3.0, 7.0),
            'phase': random.uniform(0, math.pi * 2),
            'rate': random.uniform(0.05, 0.12),
            'color': random.choice(self.GLINT_COLORS),


        } for _ in range(10)]
        self._twinkle_frame = 0

    def _lerp_rgb(self, a, b, t):
        return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))



    def _draw_anime(self, w, h):
        base = self.state_tint
        top = self._lerp_rgb(base, tuple(
            min(255, int(c * m)) for c, m in zip(base, self.SKY_TOP)), 0.55)
        bot = self._lerp_rgb(base, tuple(
            min(255, int(c * m)) for c, m in zip(base, self.SKY_BOTTOM)), 0.45)

        N = 16
        for i in range(N):
            t = i / (N - 1)
            r, g, b = self._lerp_rgb(top, bot, t)
            self.create_rectangle(0, int(i * h / N),
                                  w, int((i + 1) * h / N) + 1,
                                  fill=f"#{r:02x}{g:02x}{b:02x}", outline="")

            

        self._draw_moon(w, h)
        self._draw_hills(w, h, base)
        self._draw_petals(w, h)
        self._draw_glints(w, h)

    def _draw_moon(self, w, h):
        cx, cy = w * self.MOON_POS[0], h * self.MOON_POS[1]
        r = max(11, min(19, h * 0.16))



        rr = r * 1.38
        self.create_oval(cx - rr, cy - rr, cx + rr, cy + rr,
                         fill="#ffe9f4", outline="", stipple="gray50")
        glow = 0.90 + math.sin(self._frame * 0.03) * 0.10
        self.create_oval(cx - r, cy - r, cx + r, cy + r,
                         fill=self._rgb(255 * glow, 250 * glow, 242 * glow),
                         outline="")
        # Soft maria so the disc isn't a flat circle.
        for fx, fy, fr in ((-0.30, -0.16, 0.36), (0.24, 0.28, 0.26),
                           (0.04, -0.44, 0.19)):
            m = 0.90
            self.create_oval(cx + r * fx - r * fr, cy + r * fy - r * fr,
                             cx + r * fx + r * fr, cy + r * fy + r * fr,
                             fill=self._rgb(238 * glow, 230 * glow,
                                            226 * glow * m),
                             outline="", stipple="gray50")



    @staticmethod
    def _rgb(r, g, b):
        c = [max(0, min(255, int(round(v)))) for v in (r, g, b)]
        return "#%02x%02x%02x" % tuple(c)

    def _draw_hills(self, w, h, base):
        """Silhouette layers for depth — the classic anime horizon."""
        br = max(9, min(22, h // 6))



        layers = ((0.80, 0.26, 0.0, 0.30), (0.99, 0.20, 1.9, 0.82))
        for base_y, amp, phase, haze in layers:
            col = self._lerp_rgb(base, (255, 186, 214), haze) if haze < 0.5 \
                else self._lerp_rgb(base, (14, 7, 26), haze)
            pts = [0, h + 2]
            steps = 22
            for i in range(steps + 1):
                x = w * i / steps
                wave = math.sin(i * 0.42 + phase) * amp * br \
                    + math.sin(i * 0.19 + phase * 1.4) * amp * br * 0.5
                pts += [x, h - br * base_y - wave]
            self.create_polygon(pts, fill=self._rgb(*col), outline="")



    def _draw_petals(self, w, h):
        for p in self._petals:
            p['y'] += p['vy']
            p['x'] += p['vx'] + math.sin(
                self._frame * p['sway_rate'] + p['sway_phase']) * p['sway'] * 0.12
            p['rot'] += p['spin']
            if p['y'] > h + 10 or p['x'] < -30 or p['x'] > w + 30:
                p['y'] = -10
                p['x'] = random.uniform(-20, w + 20)


            squash = abs(math.cos(p['rot'])) * 0.42 + 0.58
            r = p['r']
            kw = {"fill": p['color'], "outline": ""}
            if p['alpha'] < 0.55:
                kw["stipple"] = "gray50"
            self.create_oval(p['x'] - r * squash, p['y'] - r * 0.82,
                             p['x'] + r * squash, p['y'] + r * 0.82, **kw)



    def _draw_glints(self, w, h):
        """Four-point sparkle stars — one pops at a time for a twinkle."""
        t = self._frame * 0.05
        for i, g in enumerate(self._glints):
            pulse = math.sin(t + g['phase']) * 0.5 + 0.5
            if pulse < 0.45:
                continue
            k = (pulse - 0.45) / 0.55
            r = g['r'] * (0.4 + k)
            stip = "gray50" if k < 0.65 else None
            kw = {"fill": g['color'], "width": 1}
            if stip:
                kw["stipple"] = stip
            self.create_line(g['x'] - r, g['y'], g['x'] + r, g['y'], **kw)
            self.create_line(g['x'], g['y'] - r, g['x'], g['y'] + r, **kw)
            d = r * 0.42
            self.create_line(g['x'] - d, g['y'] - d,
                             g['x'] + d, g['y'] + d, **kw)
            self.create_line(g['x'] - d, g['y'] + d,
                             g['x'] + d, g['y'] - d, **kw)