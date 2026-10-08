import math
import random


def start_fx(av, kind):
    s = av.size
    if kind.startswith("talk"):
        frames = 120
        parts = kind.split(":")
        if len(parts) > 1 and parts[1].isdigit():
            frames = max(30, min(400, int(parts[1])))
        av._fx["talk"] = frames
        return
    if kind == "sparkle":
        for _ in range(26):
            ang = random.uniform(0, math.pi * 2)
            sp = random.uniform(1.5, 4.5)
            av._fx["sparkles"].append({
                "x": s // 2, "y": s // 2,
                "vx": math.cos(ang) * sp, "vy": math.sin(ang) * sp - 1,
                "life": random.randint(30, 55), "max": 55,
            })
    elif kind == "fireworks":
        av._fx["bangs"].append({"n": 0, "timer": 0})
    elif kind == "orbit":
        av._fx["orbit"] = 110
    elif kind == "heartrain":
        av._fx["rain"] = 100
    elif kind == "music":
        av._fx["music"] = 100
    elif kind == "rainbow":
        av._fx["rainbow"] = 110
    elif kind == "giggle":
        av._fx["giggle"] = 80
    elif kind == "zoomies":
        av._fx["zoom"] = 90




def update_fx(av):
    s = av.size
    fx = av._fx
    for p in fx["sparkles"]:
        p["x"] += p["vx"]; p["y"] += p["vy"]; p["vy"] += 0.08
        p["life"] -= 1
    fx["sparkles"] = [p for p in fx["sparkles"] if p["life"] > 0]
    if fx["bangs"]:
        b = fx["bangs"][0]
        b["timer"] -= 1
        if b["timer"] <= 0 and b["n"] < 4:
            b["n"] += 1
            b["timer"] = 22
            bx = random.uniform(s * 0.2, s * 0.8)
            by = random.uniform(s * 0.1, s * 0.5)
            col = random.choice(("#f9e2af", "#f5c2e7", "#89dceb",
                                 "#a6e3a1", "#cba6f7"))
            for _ in range(14):
                ang = random.uniform(0, math.pi * 2)
                sp = random.uniform(1, 3.5)
                fx["fire"].append({
                    "x": bx, "y": by,
                    "vx": math.cos(ang) * sp, "vy": math.sin(ang) * sp,
                    "life": 35, "color": col,
                })





        if b["n"] >= 4 and b["timer"] <= -40:
            fx["bangs"].pop(0)
    for p in fx["fire"]:
        p["x"] += p["vx"]; p["y"] += p["vy"]
        p["vx"] *= 0.97; p["vy"] *= 0.97; p["vy"] += 0.03
        p["life"] -= 1
    fx["fire"] = [p for p in fx["fire"] if p["life"] > 0]
    for key in ("orbit", "rain", "music", "rainbow", "giggle", "zoom",
                "talk"):
        if fx.get(key, 0) > 0:
            fx[key] -= 1




    if fx["rain"] > 0 and av._frame % 4 == 0:
        fx["drops"].append({
            "x": random.uniform(0, s), "y": -6,
            "vy": random.uniform(1.5, 3), "life": 80,
            "size": random.randint(7, 12),
        })
    for d in fx["drops"]:
        d["y"] += d["vy"]; d["life"] -= 1
    fx["drops"] = [d for d in fx["drops"] if d["life"] > 0 and d["y"] < s + 8]
    if fx["music"] > 0 and av._frame % 10 == 0:
        fx["notes"].append({
            "x": s // 2 + random.uniform(-14, 14),
            "y": s // 2 - s * 0.3,
            "life": 45, "size": random.randint(8, 13),
        })
    for n in fx["notes"]:
        n["y"] -= 1.1; n["life"] -= 1
    fx["notes"] = [n for n in fx["notes"] if n["life"] > 0]




def draw_fx(av):
    s = av.size
    cx = s // 2
    cy = s // 2 + 1
    body_r = int(s * 0.36)
    fx = av._fx
    for p in fx["sparkles"]:
        t = max(0.0, p["life"] / p["max"])
        sz = max(4, int(9 * t))
        av.create_text(p["x"], p["y"], text="✦", fill="#fff3b0",
                       font=("Segoe UI", sz))
    for p in fx["fire"]:
        r = max(1, int(3 * p["life"] / 35))
        av.create_oval(p["x"] - r, p["y"] - r,
                       p["x"] + r, p["y"] + r,
                       fill=p["color"], outline="")

        
    if fx.get("orbit", 0) > 0:
        ring = body_r + 10
        n = 7




        for i in range(n):


            ang = av._frame * 0.12 + i * math.pi * 2 / n
            x = cx + math.cos(ang) * ring
            y = cy + math.sin(ang) * ring * 0.55
            sz = 6 if i % 2 else 8
            av.create_text(x, y, text="★", fill="#f9e2af",
                           font=("Segoe UI", sz))
    for d in fx["drops"]:
        av.create_text(d["x"], d["y"], text="♥", fill="#ff8fab",
                       font=("Segoe UI", d["size"]))
    for n in fx["notes"]:
        av.create_text(n["x"], n["y"], text="♪", fill="#89dceb",
                       font=("Segoe UI", n["size"]))
    if fx.get("rainbow", 0) > 0:
        cols = ("#f38ba8", "#fab387", "#f9e2af", "#a6e3a1",
                "#89dceb", "#cba6f7")
        for i, c in enumerate(cols):
            r = body_r + 6 + i * 3
            start = 180 + math.sin(av._frame * 0.08) * 8
            av.create_arc(cx - r, cy - r, cx + r, cy + r,
                          start=start, extent=180, style="arc",
                          outline=c, width=2.5)


            
    if fx.get("giggle", 0) > 0:
        off = math.sin(av._frame * 0.6) * 3
        av.create_text(cx + body_r + 4 + off, cy - body_r,
                       text="≧◡≦", fill="#ffffff",
                       font=("Segoe UI", 8, "bold"))
    if fx.get("zoom", 0) > 0:
        w = body_r + 14
        for i in range(3):
            y = cy + (i - 1) * 14 + math.sin(av._frame * 0.5 + i) * 2
            av.create_line(cx - w, y, cx - w + 10, y,
                           fill="#a6e3a1", width=2)
            av.create_line(cx + w, y, cx + w - 10, y,
                           fill="#a6e3a1", width=2)
    if fx.get("talk", 0) > 0:
        flap = abs(math.sin(av._frame * 0.55))
        mh = 2 + int(flap * 6)
        mw = int(s * 0.06) + 2
        my = cy + int(s * 0.12)
        av.create_oval(cx - mw, my - mh, cx + mw, my + mh,
                       fill="#2b2438", outline="")
        av.create_oval(cx - mw // 2, my + mh // 3,
                       cx + mw // 2, my + mh,
                       fill="#ff8fab", outline="")
        for i in range(2):
            r = body_r + 6 + i * 6 + int(flap * 3)
            av.create_arc(cx + body_r - 4, cy - r,
                          cx + body_r + 12, cy + r,
                          start=270, extent=110, style="arc",
                          outline="#89dceb", width=2)
