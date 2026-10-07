import math

PIXEL_CAT_PATTERN = [
    ".X......X.",
    ".XX....XX.",
    ".XXXXXXXX.",
    ".XX.XX.XX.",
    ".XXXXXXXX.",
    ".XXXXXXXX.",
    "..XXXXXX..",
    "...XXXX...",
]
PIXEL_CAT_EYES = [(3, 3), (3, 6)]
PIXEL_CAT_NOSE = [(5, 4), (5, 5)]





def draw_pixel_cat(canvas, size, frame, blinking):
    from agent.desktop_widget.config import mix
    canvas.delete("all")
    s = size
    body_dark = "#0a0a14"
    body_light = "#1f1f2e"
    pad = 2
    canvas.create_rectangle(pad, pad, s - pad, s - pad,
                            fill=body_dark, outline=body_light, width=1)
    sp = 5
    canvas.create_rectangle(sp, sp, s - sp, s - sp,
                            fill="#0a1810", outline="")
    for y in range(sp + 2, s - sp - 1, 3):
        canvas.create_line(sp + 1, y, s - sp - 1, y,
                           fill="#0d2415", width=1)


        

    cols, rows = 10, 8
    gw = (s - 2 * sp - 2) / cols
    gh = (s - 2 * sp - 2) / rows
    sx, sy = sp + 1, sp + 1




    breathe = math.sin(frame * 0.05) * 0.5 + 0.5
    pixel_color = mix("#5fa370", "#a6f5b0", breathe)
    eye_color = "#dff5d0" if not blinking else "#5fa370"

    for r, row in enumerate(PIXEL_CAT_PATTERN):
        for col, ch in enumerate(row):
            if ch == 'X':
                x = sx + col * gw
                y = sy + r * gh
                if (r + col + frame // 4) % 11 == 0:
                    c = mix(pixel_color, "#dff5d0", 0.5)
                else:
                    c = pixel_color
                canvas.create_rectangle(x, y, x + gw + 1, y + gh + 1,
                                        fill=c, outline="")

                


                

    for (r, col) in PIXEL_CAT_EYES:
        x = sx + col * gw
        y = sy + r * gh
        if blinking:
            canvas.create_rectangle(x, y + gh * 0.4,
                                    x + gw + 1, y + gh * 0.6 + 1,
                                    fill="#1a3a20", outline="")
        else:
            look = math.sin(frame * 0.03) * gw * 0.15
            canvas.create_rectangle(x + look, y,
                                    x + gw + 1 + look, y + gh + 1,
                                    fill=eye_color, outline="")
            canvas.create_rectangle(x + gw * 0.2 + look, y + gh * 0.15,
                                    x + gw * 0.5 + look, y + gh * 0.45,
                                    fill="#ffffff", outline="")

    for (r, col) in PIXEL_CAT_NOSE:
        x = sx + col * gw
        y = sy + r * gh
        canvas.create_rectangle(x + gw * 0.2, y + gh * 0.2,
                                x + gw * 0.8 + 1, y + gh * 0.8 + 1,
                                fill="#f5a3b5", outline="")

    glow_pulse = math.sin(frame * 0.04) * 0.3 + 0.7
    glow_c = mix("#000000", "#5fa370", glow_pulse * 0.4)
    for i in range(3):
        canvas.create_rectangle(pad - 1 - i, pad - 1 - i,
                                s - pad + 1 + i, s - pad + 1 + i,
                                outline=glow_c, width=1, stipple="gray25")

    if frame % 200 > 180:
        zx = s - 8
        zy = 8 + math.sin(frame * 0.1) * 2
        canvas.create_text(zx, zy, text="z", fill="#a6f5b0",
                           font=("Segoe UI", 7, "bold"))