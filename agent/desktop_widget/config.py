import json
import os

CONFIG_FILE = os.path.expanduser("~/.config/kibo/widget_config.json")

DEFAULT_CONFIG = {
    "width": 2100,
    "idle_width": 100,
    "height": 120,
    "avatar_size": 96,
    "y": 0,
    "bg_color": "#0a0a18",
    "fg_color": "#cdd6f4",
    "accent_color": "#89b4fa",
    "working_color": "#f9e2af",
    "approval_color": "#f38ba8",
    "idle_color": "#a6e3a1",
    "tool_color": "#94e2d5",
    "font_size": 13,
    "opacity": 0.97,
    "poll_interval": 1.0,
    "api_base": "http://127.0.0.1:5000",
    "pixel_screensaver_seconds": 45,
}


def migrate_config(cfg):
    if "avatar_size" not in cfg:
        cfg["avatar_size"] = DEFAULT_CONFIG["avatar_size"]
        cfg["idle_width"] = DEFAULT_CONFIG["idle_width"]
        cfg["height"] = DEFAULT_CONFIG["height"]
        cfg["width"] = max(cfg.get("width", 0), DEFAULT_CONFIG["width"])
        if cfg.get("font_size", 11) < 12:
            cfg["font_size"] = DEFAULT_CONFIG["font_size"]
    avatar = max(40, int(cfg.get("avatar_size", 100)))
    if cfg.get("height", 0) < avatar + 24:
        cfg["height"] = avatar + 24
    if cfg.get("idle_width", 0) < avatar + 36:
        cfg["idle_width"] = avatar + 36
    if cfg.get("width", 0) < cfg["idle_width"] + 320:
        cfg["width"] = cfg["idle_width"] + 580
    return cfg


def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE) as f:
                cfg = {**DEFAULT_CONFIG, **json.load(f)}
                return migrate_config(cfg)
        except Exception:
            pass
    return DEFAULT_CONFIG.copy()




def save_config(cfg):
    os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        json.dump(cfg, f, indent=2)



def shade(hex_color, factor):
    r, g, b = (int(hex_color[i:i + 2], 16) for i in (1, 3, 5))
    if factor >= 0:
        r, g, b = (int(c + (255 - c) * factor) for c in (r, g, b))
    else:
        r, g, b = (int(c * (1 + factor)) for c in (r, g, b))
    return f"#{r:02x}{g:02x}{b:02x}"


def mix(c1, c2, t):
    r1, g1, b1 = (int(c1[i:i + 2], 16) for i in (1, 3, 5))
    r2, g2, b2 = (int(c2[i:i + 2], 16) for i in (1, 3, 5))
    r = int(r1 + (r2 - r1) * t)
    g = int(g1 + (g2 - g1) * t)
    b = int(b1 + (b2 - b1) * t)
    return f"#{r:02x}{g:02x}{b:02x}"