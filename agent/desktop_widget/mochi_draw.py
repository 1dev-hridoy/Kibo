import math

from agent.desktop_widget.config import shade, mix


def draw_mochi(av):
    av.delete("all")
    s = av.size
    ink = av.INK
    cx = s // 2
    cy = s // 2 + 1
    body_r = int(s * 0.36)
    color = av.colors.get(av.state, av.colors["idle"])

    if av.state == "idle":
        bounce = math.sin(av._frame * 0.1) * 1.2
    elif av.state == "working":
        bounce = math.sin(av._frame * 0.3) * 2.2
    elif av.state == "happy":
        bounce = abs(math.sin(av._frame * 0.5)) * 4
    elif av.state == "sleepy":
        bounce = math.sin(av._frame * 0.06) * 0.6
    else:
        bounce = abs(math.sin(av._frame * 0.2)) * 3
    if av._hovering and av.state == "idle":
        bounce += 0.8

    squish = math.sin(av._frame * 0.1 + 1.5) * 0.04
    click_sq = getattr(av, "_squish", 0.0)
    rx = body_r * (1 + squish + click_sq * 0.35)
    ry = body_r * (1 - squish - click_sq * 0.28)
    if av.state == "dizzy":
        cx = cx + math.sin(av._frame * 0.8) * 4
    cy_b = cy + bounce

    flip_scale = 1.0
    if av._fx.get("flip", 0) > 0:
        prog = 1.0 - av._fx["flip"] / 100.0
        ang = prog * math.pi * float(av._fx.get("flip_dir", 1))
        flip_scale = math.cos(ang)



        if flip_scale > 0:
            flip_scale = flip_scale * 0.25 + 0.75


        else:
            flip_scale = abs(flip_scale)
        rx *= max(0.08, flip_scale)
        lift = abs(math.sin(prog * math.pi)) * s * 0.42
        cy_b -= lift




    halo_pulse = math.sin(av._frame * 0.05) * 0.3 + 0.7
    for i in range(3):
        halo_r = body_r + 3 + i * 3.5
        alpha = (1 - i / 3) * halo_pulse
        halo_c = mix(av.base_bg, color, alpha * 0.35)
        stip = "gray25" if i > 1 else "gray50"
        av.create_oval(cx - halo_r, cy_b - halo_r,
                       cx + halo_r, cy_b + halo_r,
                       fill=halo_c, outline="", stipple=stip)

    if av.state in ("working", "approval", "happy"):
        ring_r = body_r + 6
        seg_count = 12
        active_segs = 4
        rotation = av._frame * 0.05
        for i in range(seg_count):
            ang = (i / seg_count) * math.pi * 2 + rotation
            seg_idx = int((i + av._frame * 0.1) % seg_count)
            if seg_idx < active_segs:
                ax = cx + math.cos(ang) * ring_r
                ay = cy_b + math.sin(ang) * ring_r
                av.create_oval(ax - 1.8, ay - 1.8,
                               ax + 1.8, ay + 1.8,
                               fill=color, outline="")




    if av.state in ("working", "happy", "approval"):
        wag_amp = 9 if av.state == "happy" else 5
        wag_speed = 0.5 if av.state == "happy" else 0.25
        tail_wag = math.sin(av._frame * wag_speed) * wag_amp
        tx = cx - rx * 0.4
        ty = cy_b + ry * 0.5
        tail_c = shade(color, -0.05)
        av.create_line(tx, ty,
                       tx - 4 + tail_wag * 0.5, ty + 5,
                       tx - 9 + tail_wag, ty - 1,
                       smooth=True, fill=tail_c, width=3,
                       capstyle="round")
        




    ear_outer = shade(color, -0.12)
    ear_inner = "#f5a3b5"
    wiggle = math.sin(av._frame * 0.15) * 0.6 if av.state != "idle" else 0
    if av._hovering:
        wiggle += 0.5
    for side in (-1, 1):
        ex = cx + side * rx * 0.62
        top = cy_b - ry - s * 0.13 + wiggle * side
        av.create_polygon(ex - side * s * 0.17, cy_b - ry * 0.48,
                          ex + side * s * 0.03, top,
                          ex + side * s * 0.15, cy_b - ry * 0.38,
                          fill=ear_outer, outline="", smooth=True)
        av.create_polygon(ex - side * s * 0.08, cy_b - ry * 0.48,
                          ex + side * s * 0.01, top + s * 0.07,
                          ex + side * s * 0.07, cy_b - ry * 0.43,
                          fill=ear_inner, outline="", smooth=True)



        




    sh = s * 0.20 - bounce * 0.5
    sh_lift = 1.0
    if av._fx.get("flip", 0) > 0:
        prog = 1.0 - av._fx["flip"] / 100.0

        
        sh_lift = 1.0 - abs(math.sin(prog * math.pi)) * 0.62
    sh *= sh_lift
    av.create_oval(cx - sh * 1.4, s - 4, cx + sh * 1.4, s - 2,
                   fill=shade(color, -0.55), outline="",
                   stipple="gray25")

    av.create_oval(cx - rx, cy_b - ry, cx + rx, cy_b + ry,
                   fill=color, outline="")
    av.create_oval(cx - rx * 0.65, cy_b - ry * 0.85,
                   cx - rx * 0.15, cy_b - ry * 0.45,
                   fill=shade(color, 0.55), outline="",
                   stipple="gray50")



    

    if av.state in ("working", "happy", "approval"):
        wh_y = cy_b + ry * 0.25
        wh_color = shade(ink, 0.4)
        for side in (-1, 1):
            base_x = cx + side * rx * 0.42
            for i, dy in enumerate((-3, 0, 3)):
                end_x = base_x + side * (rx * 0.6 + 3)
                end_y = wh_y + dy + math.sin(av._frame * 0.1 + i) * 0.5
                av.create_line(base_x, wh_y + dy * 0.4,
                               end_x, end_y,
                               fill=wh_color, width=1, capstyle="round")

    eye_r = s * 0.12
    eye_y = cy_b + ry * 0.05
    eyespace = rx * 0.52




    if av._yawning:
        for ex in (cx - eyespace, cx + eyespace):
            av.create_arc(ex - eye_r, eye_y - eye_r * 0.4,
                          ex + eye_r, eye_y + eye_r * 0.8,
                          start=20, extent=140, style="arc",
                          outline=ink, width=2)
    elif av._blinking or av.state == "sleepy" or \
            (av.state == "idle" and av._frame % 200 > 188):
        for ex in (cx - eyespace, cx + eyespace):
            av.create_arc(ex - eye_r, eye_y - eye_r * 0.6,
                          ex + eye_r, eye_y + eye_r * 1.1,
                          start=20, extent=140, style="arc",
                          outline=ink, width=2)
    elif av.state == "happy":
        for ex in (cx - eyespace, cx + eyespace):
            av.create_arc(ex - eye_r * 1.1, eye_y - eye_r * 0.5,
                           ex + eye_r * 1.1, eye_y + eye_r * 1.2,
                           start=20, extent=140, style="arc",
                           outline=ink, width=2.2)
            av.create_text(ex + eye_r * 1.4, eye_y - eye_r * 0.9,
                            text="✦", fill="#fff3b0",
                            font=("Segoe UI", 7))


            
    elif av.state == "annoyed":
        for ex in (cx - eyespace, cx + eyespace):
            av.create_line(ex - eye_r * 0.8, eye_y - eye_r * 0.8,
                           ex + eye_r * 0.8, eye_y + eye_r * 0.8,
                           fill=ink, width=2.2, capstyle="round")
            av.create_line(ex - eye_r * 0.8, eye_y + eye_r * 0.8,
                           ex + eye_r * 0.8, eye_y - eye_r * 0.8,
                           fill=ink, width=2.2, capstyle="round")


            
    elif av.state == "dizzy":
        for ex in (cx - eyespace, cx + eyespace):
            pts = []
            for k in range(26):
                ang = k * 0.55 + av._frame * 0.05
                r = 1 + k * 0.26
                pts += [ex + math.cos(ang) * r,
                        eye_y + math.sin(ang) * r * 0.8]
            av.create_line(*pts, fill=ink, width=1.6, smooth=True)
    else:
        for ex in (cx - eyespace, cx + eyespace):
            if av._hovering:
                dx = av._mouse_x - ex
                dy = av._mouse_y - eye_y
                dist = math.hypot(dx, dy) + 0.001
                max_off = eye_r * 0.35
                lx = (dx / dist) * min(max_off, dist * 0.2)
                ly = (dy / dist) * min(max_off, dist * 0.2)
            else:
                lx = math.sin(av._frame * 0.04) * 1.0
                ly = 0
            av.create_oval(ex - eye_r, eye_y - eye_r * 1.15,
                           ex + eye_r, eye_y + eye_r * 1.15,
                           fill=ink, outline="")
            hl = eye_r * 0.55
            av.create_oval(ex - eye_r * 0.7 + lx,
                           eye_y - eye_r * 0.95 + ly,
                           ex - eye_r * 0.7 + hl + lx,
                           eye_y - eye_r * 0.95 + hl + ly,
                           fill="white", outline="")
            hl2 = eye_r * 0.28
            av.create_oval(ex + eye_r * 0.25 + lx,
                           eye_y + eye_r * 0.4 + ly,
                           ex + eye_r * 0.25 + hl2 + lx,
                           eye_y + eye_r * 0.4 + hl2 + ly,
                           fill="white", outline="")








    nose_y = eye_y + eye_r * 1.8
    nose_w = s * 0.045
    av.create_polygon(cx - nose_w, nose_y,
                      cx + nose_w, nose_y,
                      cx, nose_y + nose_w * 1.5,
                      fill="#ff8fab", outline="", smooth=True)





    if av.state == "happy":
        cheek_c = "#ffafcc"
    elif av.state == "approval":
        cheek_c = "#ffb3c6"
    elif av.state == "sleepy":
        cheek_c = "#f5a3b5"
    else:
        cheek_c = "#ff8fab"
    cr = s * 0.075
    cheek_y = eye_y + eye_r * 1.55
    for side in (-1, 1):
        bx = cx + side * (eyespace + eye_r * 0.9)
        av.create_oval(bx - cr * 1.3, cheek_y - cr * 0.7,
                       bx + cr * 1.3, cheek_y + cr * 0.7,
                       fill=cheek_c, outline="", stipple="gray50")
        




    brow_y = eye_y - eye_r * 1.7
    if av.state == "approval":
        av.create_line(cx - eyespace - eye_r, brow_y + 2,
                       cx - eyespace + eye_r, brow_y - 2,
                       fill=ink, width=2)
        av.create_line(cx + eyespace - eye_r, brow_y - 2,
                       cx + eyespace + eye_r, brow_y + 2,
                       fill=ink, width=2)
    elif av.state == "working":
        av.create_line(cx - eyespace - eye_r, brow_y + 1,
                       cx - eyespace + eye_r, brow_y - 1,
                       fill=ink, width=2)
        av.create_line(cx + eyespace - eye_r, brow_y - 1,
                       cx + eyespace + eye_r, brow_y + 1,
                       fill=ink, width=2)






    my = nose_y + nose_w * 2.0
    mw = s * 0.07
    if av._yawning:
        yw = s * 0.10
        yh = s * 0.14
        av.create_oval(cx - yw, my - yh * 0.5, cx + yw, my + yh,
                       fill=ink, outline="")
        av.create_oval(cx - yw * 0.5, my + yh * 0.3,
                       cx + yw * 0.5, my + yh * 0.9,
                       fill="#ff8fab", outline="")


        
    elif av.state == "idle":
        av.create_arc(cx - mw * 2, my - mw, cx, my + mw,
                      start=200, extent=160, style="arc",
                      outline=ink, width=1.6)
        av.create_arc(cx, my - mw, cx + mw * 2, my + mw,
                      start=180, extent=160, style="arc",
                      outline=ink, width=1.6)

        

    elif av.state == "happy":
        av.create_arc(cx - mw * 2, my - mw * 1.5,
                      cx + mw * 2, my + mw * 1.5,
                      start=10, extent=160, style="chord",
                      fill=ink, outline=ink, width=1.5)
        av.create_oval(cx - mw * 0.6, my + mw * 0.3,
                       cx + mw * 0.6, my + mw * 1.3,
                       fill="#ff8fab", outline="")


        
    elif av.state == "working":
        r = s * 0.035 + abs(math.sin(av._frame * 0.3)) * 1.0
        av.create_oval(cx - r, my - r + 1, cx + r, my + r + 1,
                       fill=ink, outline="")

        
    elif av.state == "sleepy":
        av.create_line(cx - mw, my, cx + mw, my,

                       
                        fill=ink, width=1.6, capstyle="round")

        
    elif av.state == "annoyed":
        pts = []
        for i in range(5):
            px = cx - mw + i * (mw / 2)
            py = my + (3 if i % 2 == 0 else -3)
            pts += [px, py]
        av.create_line(*pts, fill=ink, width=1.8, capstyle="round")



    elif av.state == "dizzy":
        r = s * 0.045
        av.create_oval(cx - r, my - r, cx + r, my + r,
                       fill=ink, outline="")
    else:
        av.create_oval(cx - mw, my - mw * 0.5, cx + mw, my + mw * 1.4,
                       fill=ink, outline="")
        av.create_oval(cx - mw * 0.55, my + mw * 0.55,
                       cx + mw * 0.55, my + mw * 1.3,
                       fill="#ff8fab", outline="")
        






    if av.state == "idle" and av._sleep_z > 0 and not av._yawning:
        for i in range(av._sleep_z):
            zx = cx + rx + 4 + i * 5
            zy = cy_b - ry - 2 - i * 5
            fade = 140 + i * 30
            av.create_text(zx, zy, text="z",
                           font=("Segoe UI", 7 + i * 2),
                           fill=f"#{fade:02x}{fade:02x}00")
            




    if av.state == "sleepy":
        for i in range(3):
            zx = cx + rx + 4 + i * 7 + \
                 math.sin(av._frame * 0.05 + i) * 2
            zy = cy_b - ry - 2 - i * 8
            sz = 9 + i * 3
            alpha = 200 - i * 40
            av.create_text(zx, zy, text="Z",
                           font=("Segoe UI", sz, "bold"),
                           fill=f"#{alpha:02x}{alpha:02x}{alpha:02x}")
            

    if av.state == "working":
        for i in range(2):
            ang = av._frame * 0.12 + i * math.pi
            sx = cx + math.cos(ang) * (rx + 5)
            sy = cy_b - ry * 0.5 + math.sin(ang) * (ry * 0.7)
            twinkle = 5 + int(abs(math.sin(av._frame * 0.25 + i)) * 3)
            av.create_text(sx, sy, text="✦", fill="#fff3b0",
                           font=("Segoe UI", twinkle))

    if av.state == "approval":
        dy = (av._frame % 20) * 0.3
        av.create_oval(cx + rx - 3, cy_b - ry + 3 + dy,
                       cx + rx + 1, cy_b - ry + 9 + dy,
                       fill="#89dceb", outline="")
        av.create_text(cx - rx - 2, cy_b - ry - 1 - bounce * 0.5,
                       text="!", fill="#ffffff",
                       font=("Segoe UI", 9, "bold"))



    if av._wave_timer > 0:
        wave_x = cx + rx + 8
        wave_y = cy_b - ry
        wave_off = math.sin(av._frame * 0.4) * 3
        av.create_text(wave_x, wave_y + wave_off, text="👋",
                       font=("Segoe UI", 12))

    for h in av._hearts:
        t = max(0.0, h['life'] / 45)
        c = mix(av.base_bg, "#ff6b95", t)
        sz = max(6, int(h['size'] * (0.5 + t * 0.5)))
        av.create_text(h['x'], h['y'], text="♥",
                       fill=c, font=("Segoe UI", sz))

    for c in av._confetti:
        t = max(0.0, c['life'] / 60)
        sz = max(3, int(c['size'] * t))
        av.create_oval(c['x'] - sz, c['y'] - sz,
                       c['x'] + sz, c['y'] + sz,
                       fill=c['color'], outline="")