import math
import random


def start_fx(av, kind):
    s = av.size
    if kind == "talk" or kind.startswith("talk:"):
        frames = 120
        parts = kind.split(":")
        if len(parts) > 1 and parts[1].isdigit():
            frames = max(30, min(400, int(parts[1])))
        av._fx["talk"] = frames
        return
    elif kind in ("water", "grass", "stretch", "eyes", "posture"):
        av._fx[kind] = 140
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
    elif kind == "newtrack":
        av._fx["newtrack"] = 90
        for _ in range(18):
            ang = random.uniform(0, math.pi * 2)
            sp = random.uniform(2.0, 5.0)
            av._fx["sparkles"].append({


                "x": s // 2, "y": s // 2,
                "vx": math.cos(ang) * sp, "vy": math.sin(ang) * sp - 1.5,
                "life": random.randint(35, 65), "max": 65,
            })



    elif kind in ("ytwave", "ytplay", "ytbars",
                  "spwave", "spbars", "spnote"):
        av._fx[kind] = 80
    elif kind == "flip":


        av._fx["flip"] = 100
        av._fx["flip_dir"] = random.choice((-1, 1))
    elif kind == "coinflip":
        av._fx["coinflip"] = 130


        av._fx["coin_face"] = random.choice(("heads", "tails"))
        av._fx["coin_spin"] = 0
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
                "talk", "water", "grass", "stretch", "eyes", "posture",
                "newtrack", "ytwave", "ytplay", "ytbars",
                "spwave", "spbars", "spnote",
                "flip", "coinflip"):
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
    if fx.get("spnote", 0) > 0 and av._frame % 9 == 0:
        fx["notes"].append({
            "x": s // 2 + random.uniform(-16, 16),
            "y": s // 2 - s * 0.3,
            "life": 50, "size": random.randint(9, 14),
            "color": "#1db954",
        })
    if fx.get("music", 0) > 0 and av._frame % 10 == 0:
        fx["notes"].append({
            "x": s // 2 + random.uniform(-14, 14),
            "y": s // 2 - s * 0.3,
            "life": 45, "size": random.randint(8, 13),
            "color": "#89dceb",
        })
    for n in fx["notes"]:
        n["y"] -= 1.1; n["life"] -= 1
    fx["notes"] = [n for n in fx["notes"] if n["life"] > 0]
    if fx.get("water", 0) > 0 and av._frame % 5 == 0:
        fx["wdrops"].append({
            "x": av.size // 2 + random.uniform(-22, 22),
            "y": -6, "vy": random.uniform(2, 3.5), "life": 70,
        })
    for d in fx["wdrops"]:
        d["y"] += d["vy"]; d["life"] -= 1
    fx["wdrops"] = [d for d in fx["wdrops"]
                    if d["life"] > 0 and d["y"] < av.size + 8]




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
        av.create_text(n["x"], n["y"], text="♪",
                       fill=n.get("color", "#89dceb"),
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
    if fx.get("water", 0) > 0:
        for d in fx["wdrops"]:
            x, y = d["x"], d["y"]
            av.create_oval(x - 3, y - 1, x + 3, y + 5,
                           fill="#89dceb", outline="")
            av.create_polygon(x - 3, y + 1, x + 3, y + 1, x, y - 5,
                              fill="#89dceb", outline="")
        ripple = (av._frame % 30) / 30
        rw = 4 + ripple * 14
        av.create_oval(cx - rw, s - 8 - ripple * 2,
                       cx + rw, s - 4 - ripple * 2,
                       outline="#89dceb", width=1)
        av.create_text(cx, 10, text="drink up!", fill="#89dceb",
                       font=("Segoe UI", 7, "bold"))

        
    if fx.get("grass", 0) > 0:
        gy = s - 3
        for i in range(7):
            bx = cx - 30 + i * 10
            sway = math.sin(av._frame * 0.15 + i * 0.9) * 3
            h = 12 + (i % 3) * 4
            av.create_line(bx, gy, bx + sway, gy - h,
                           fill="#a6e3a1", width=2, capstyle="round")
        fx0 = cx + 24
        fy = gy - 16 + math.sin(av._frame * 0.1) * 1.5
        for px, py in ((fx0 - 3, fy), (fx0 + 3, fy),
                       (fx0, fy - 3), (fx0, fy + 3)):
            av.create_oval(px - 2.5, py - 2.5, px + 2.5, py + 2.5,
                           fill="#f5c2e7", outline="")
        av.create_oval(fx0 - 2, fy - 2, fx0 + 2, fy + 2,
                       fill="#f9e2af", outline="")
        av.create_oval(cx - 34, 12, cx - 24, 22,
                       fill="#f9e2af", outline="")
        av.create_text(cx, 10, text="touch grass!", fill="#a6e3a1",
                       font=("Segoe UI", 7, "bold"))


        
    if fx.get("stretch", 0) > 0:
        phase = (av._frame % 60) / 60
        rr = body_r + 4 + phase * 16
        av.create_oval(cx - rr, cy - rr, cx + rr, cy + rr,
                       outline="#cba6f7", width=2)
        av.create_text(cx, cy - body_r - 12, text="↑ stretch ↑",
                       fill="#cba6f7", font=("Segoe UI", 8, "bold"))


        
    if fx.get("eyes", 0) > 0:
        look = math.sin(av._frame * 0.12) * 4
        for ex in (cx - 13, cx + 13):
            av.create_oval(ex - 9, cy - 8, ex + 9, cy + 8,
                           fill="white", outline="#2b2438", width=1)
            av.create_oval(ex - 4 + look, cy - 4, ex + 4 + look, cy + 4,
                           fill="#2b2438", outline="")
        av.create_text(cx, 10, text="20-20-20: look far!",
                       fill="#f9e2af", font=("Segoe UI", 7, "bold"))



        
    if fx.get("posture", 0) > 0:
        bob = math.sin(av._frame * 0.2) * 2
        px = cx - body_r - 10
        av.create_line(px, cy + 18 + bob, px, cy - 18 + bob,
                       fill="#f38ba8", width=2)
        av.create_polygon(px - 4, cy - 18 + bob, px + 4, cy - 18 + bob,
                          px, cy - 24 + bob, fill="#f38ba8", outline="")
        av.create_polygon(px - 4, cy + 18 + bob, px + 4, cy + 18 + bob,
                          px, cy + 24 + bob, fill="#f38ba8", outline="")
        av.create_text(cx, 10, text="sit tall!",
                       fill="#f38ba8", font=("Segoe UI", 7, "bold"))
    if fx.get("newtrack", 0) > 0:
        t = fx["newtrack"] / 90.0
        alpha = min(1.0, t * 2)


        sz = int(10 + (1.0 - t) * 6)
        av.create_text(cx, cy - body_r - 18, text="♪ NEW ♪",
                       fill="#f9e2af", font=("Segoe UI", sz, "bold"))
        
        for i in range(3):
            ang = av._frame * 0.15 + i * math.pi * 2 / 3


            r = body_r + 14 + (1.0 - t) * 20
            x = cx + math.cos(ang) * r
            y = cy + math.sin(ang) * r * 0.5
            av.create_text(x, y, text="✦", fill="#f5c2e7",
                           font=("Segoe UI", 8))

            
    if fx.get("ytwave", 0) > 0:
        n = 14
        for i in range(n):


            ang = math.pi * 2 * i / n
            wob = math.sin(av._frame * 0.18 + i * 1.1) * 6
            r = body_r + 10 + wob


            x1 = cx + math.cos(ang) * r
            y1 = cy + math.sin(ang) * r * 0.6
            ang2 = math.pi * 2 * (i + 1) / n
            r2 = body_r + 10 + math.sin(av._frame * 0.18 + (i + 1) * 1.1) * 6


            x2 = cx + math.cos(ang2) * r2
            y2 = cy + math.sin(ang2) * r2 * 0.6
            av.create_line(x1, y1, x2, y2, fill="#ff4d4d", width=2)

    if fx.get("ytplay", 0) > 0:
        s2 = 11 + math.sin(av._frame * 0.22) * 2.5
        y = cy - body_r - 20


        av.create_polygon(cx - s2, y - s2, cx - s2, y + s2,
                          cx + s2, y, fill="#ff4d4d", outline="")


    if fx.get("ytbars", 0) > 0:
        for i in range(9):
            h = 3 + abs(math.sin(av._frame * 0.28 + i * 0.85)) * 15
            x = cx - 36 + i * 9
            av.create_rectangle(x, s - 6 - h, x + 6, s - 6,
                                fill="#ff4d4d", outline="")




    if fx.get("spwave", 0) > 0:
        r = body_r + 6 + (av._frame % 45) * 0.8
        av.create_oval(cx - r, cy - r, cx + r, cy + r,
                       outline="#1db954", width=2)


    if fx.get("spbars", 0) > 0:
        for i in range(7):
            h = 3 + abs(math.sin(av._frame * 0.32 + i * 0.9)) * 13
            x = cx - 30 + i * 10
            av.create_rectangle(x, s - 6 - h, x + 7, s - 6,
                                fill="#1db954", outline="")



    if fx.get("flip", 0) > 0:
        t = fx["flip"] / 100.0
        d = fx.get("flip_dir", 1)
        prog = 1.0 - t
        for i in range(3):
            off = i * 5
            lift = abs(math.sin(prog * math.pi)) * (10 - i * 2)


            x0 = cx - body_r - 12 - off
            y0 = cy - lift
            x1 = x0 + (6 + off) * d
            y1 = cy - lift
            av.create_line(x0, y0, x1, y1,
                           fill="#cba6f7", width=2, capstyle="round")
        ring = body_r + 12 + abs(math.sin(prog * math.pi)) * 8
        av.create_arc(cx - ring, cy - ring, cx + ring, cy + ring,
                      



                      start=200 * d, extent=140, style="arc",
                      outline="#f5c2e7", width=2)
        av.create_text(cx, cy - body_r - 14, text="↻",
                       fill="#cba6f7", font=("Segoe UI", 13, "bold"))

    if fx.get("coinflip", 0) > 0:
        total = 130
        prog = 1.0 - fx["coinflip"] / total
        coin_r = 12
        lift = 16


        rest_y = cy - body_r - coin_r - 2
        rest_y = max(coin_r + 3 + lift, min(rest_y, s - coin_r - 18))
        arc = abs(math.sin(prog * math.pi))
        coin_y = rest_y - arc * lift
        coin_x = cx + int(math.sin(prog * math.pi * 2) * 6)
        spinning = prog < 0.72






        if spinning:
            spin = (av._frame % 7) / 7.0
            wdt = max(2, int(coin_r * abs(math.cos(spin * math.pi))))
            av.create_oval(coin_x - wdt, coin_y - coin_r,
                           coin_x + wdt, coin_y + coin_r,
                           fill="#f9e2af", outline="#c9a227", width=2)
            av.create_line(coin_x - wdt - 5, coin_y - 4,
                           coin_x - wdt - 9, coin_y - 7,
                           fill="#fff3b0", width=2, capstyle="round")
            av.create_line(coin_x + wdt + 5, coin_y - 4,
                           coin_x + wdt + 9, coin_y - 7,
                           fill="#fff3b0", width=2, capstyle="round")
            



        else:
            face = fx.get("coin_face", "heads")
            av.create_oval(coin_x - coin_r - 2, coin_y - coin_r - 2,
                           coin_x + coin_r + 2, coin_y + coin_r + 2,
                           fill="#c9a227", outline="")
            av.create_oval(coin_x - coin_r, coin_y - coin_r,
                           coin_x + coin_r, coin_y + coin_r,
                           fill="#f9e2af", outline="#c9a227", width=2)
            av.create_text(coin_x, coin_y,
                           text="★" if face == "heads" else "✦",
                           fill="#8a6d3b", font=("Segoe UI", 13, "bold"))
            label_y = min(coin_y + coin_r + 12, s - 7)
            av.create_text(coin_x, label_y, text=face.upper(),


                           
                           fill="#f9e2af", font=("Segoe UI", 9, "bold"))
            if not fx.get("coin_spark", False):
                fx["coin_spark"] = True
                for _ in range(14):
                    ang = random.uniform(0, math.pi * 2)
                    sp = random.uniform(1.5, 4.0)
                    fx["sparkles"].append({
                        "x": coin_x, "y": coin_y,
                        "vx": math.cos(ang) * sp,
                        "vy": math.sin(ang) * sp,
                        "life": random.randint(20, 38), "max": 38,
                    })
        if prog > 0.9 and fx.get("coinflip", 0) <= 2:
            fx["coin_spark"] = False

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
