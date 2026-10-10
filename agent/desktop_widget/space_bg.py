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
    NEBULA_COLORS = (
        (255, 100, 200),
        (100, 150, 255),
        (200, 100, 255),
        (255, 180, 100),



    )




    

    def __init__(self, parent, base_color="#0a0a18", **kwargs):
        super().__init__(parent, highlightthickness=0, **kwargs)
        self.base_color = base_color
        self.state_tint = self.STATE_TINTS["idle"]
        self._frame = 0
        self._seeded = False
        self._last_w = 0
        self._last_h = 0
        self._stars_far = []
        self._stars_mid = []
        self._stars_near = []
        self._nebulae = []
        self._shooting_stars = []
        self.texts = []
        self.card_w = 0
        self._animate()

    def set_state_tint(self, state):
        self.state_tint = self.STATE_TINTS.get(state, self.STATE_TINTS["idle"])

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
            'color': random.choice(self.MID_STAR_COLORS),
        } for _ in range(30)]
        self._stars_near = [{
            'x': random.uniform(0, w),
            'y': random.uniform(5, h - 5),
            'r': random.uniform(1.5, 2.5),
            'vx': random.uniform(-0.30, -0.18),
            'phase': random.uniform(0, math.pi * 2),
            'color': random.choice(self.NEAR_STAR_COLORS),
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
            self._seed_space(w, h)
            self._seeded = True
            self._last_w, self._last_h = w, h

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

            





        for n in self._nebulae:
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