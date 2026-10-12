import json
import os

CONFIG_FILE = os.path.expanduser("~/.config/kibo/widget_config.json")


DEFAULT_PET = {
    "ink": "#2b2438",
    "ear_inner": "#f5a3b5",
    "nose": "#ff8fab",
    "sparkle": "#fff3b0",
    "petted": "#ff6b95",
    "tongue": "#ff6b95",
    "eye_light": "#89dceb",
    "eye_dark": "#313244",
    "blush": {
        "happy": "#ffafcc", "approval": "#ffb3c6",
        "sleepy": "#f5a3b5", "default": "#ff8fab",
    },
    "states": {
        "idle": "#a6e3a1", "working": "#f9e2af", "approval": "#f38ba8",
        "happy": "#f5c2e7", "sleepy": "#94e2d5",
        "annoyed": "#fab387", "dizzy": "#cba6f7",
    },
    "fx": ["#f9e2af", "#f5c2e7", "#89dceb", "#a6e3a1",
           "#cba6f7", "#f38ba8"],
}




def apply_pet(base, override):
    """Merge a theme's partial pet block onto DEFAULT_PET."""
    out = dict(base)
    for k, v in (override or {}).items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = {**out[k], **v}
        elif isinstance(v, list):
            out[k] = list(v)
        else:
            out[k] = v
    return out


def theme_pet(name):
    """Resolved pet palette for a theme name."""
    _, theme = resolve_theme(name)
    return apply_pet(DEFAULT_PET, theme.get("pet"))





THEMES = {
    "midnight": {
        "label": "Midnight",
        "background": "space",
        "bg_color": "#0a0a18",
        "fg_color": "#cdd6f4",
        "accent_color": "#89b4fa",
        "working_color": "#f9e2af",
        "approval_color": "#f38ba8",
        "idle_color": "#a6e3a1",
        "tool_color": "#94e2d5",
        "tints": {
            "idle": (8, 8, 22), "working": (22, 16, 10),
            "approval": (26, 10, 22), "happy": (22, 14, 28),
            "pixel": (5, 16, 10), "youtube": (64, 10, 10),
            "spotify": (29, 185, 84), "other": (10, 12, 28),
        },
    },
    "anime": {
        "label": "Anime · Sakura Night",
        "background": "anime",
        "bg_color": "#1b1033",
        "fg_color": "#ffeaf4",
        "accent_color": "#ff8fc7",
        "working_color": "#ffd479",
        "approval_color": "#ff6b8a",
        "idle_color": "#a8f0d4",
        "tool_color": "#9ee6ff",
        "tints": {
            "idle": (27, 16, 51), "working": (58, 28, 52),
            "approval": (66, 18, 42), "happy": (62, 26, 62),
            "pixel": (14, 34, 40), "youtube": (62, 14, 34),
            "spotify": (24, 74, 52), "other": (30, 18, 56),
        },





        "pet": {
            "ink": "#5a3a52",
            "ear_inner": "#ffb3d9",
            "nose": "#ff8fc7",
            "sparkle": "#fff3a8",
            "petted": "#ff7fb0",
            "tongue": "#ff7fb0",
            "eye_light": "#bfe9ff",
            "eye_dark": "#6b4a6b",
            "blush": {


                
                "happy": "#ffb8d9", "approval": "#ffa8c8",
                "sleepy": "#f9b8d4", "default": "#ff9ec9",
            },


            "states": 
            
            {
                "idle": "#a8f0d4", "working": "#ffd479", "approval": "#ff6b8a",
                "happy": "#ffc2e2", "sleepy": "#bcd4ff",
                "annoyed": "#ffb08a", "dizzy": "#d3b8ff",
            },
            "fx": ["#ffe6a8", "#ffc2e2", "#a8dcff", "#a8f0d4",
                   "#d3b8ff", "#ff9ec9"],
        },


    },
    "sakura": {
        "label": "Sakura · Soft Day",
        "background": "anime",
        "bg_color": "#3a2145",
        "fg_color": "#fff2f7",
        "accent_color": "#ffa8cf",
        "working_color": "#ffc98a",
        "approval_color": "#f2789a",
        "idle_color": "#b6ecd8",
        "tool_color": "#a8dcff",
        "tints": {
            "idle": (58, 33, 69), "working": (74, 44, 64),
            "approval": (78, 30, 54), "happy": (82, 44, 76),
            "pixel": (34, 62, 62), "youtube": (86, 32, 56),
            "spotify": (44, 80, 62), "other": (62, 38, 74),
        },



        "pet": {
            "ink": "#4a2f45",
            "ear_inner": "#f9b8d0",
            "nose": "#f490b8",
            "sparkle": "#ffeeb0",
            "petted": "#ef85ac",
            "tongue": "#ef85ac",
            "eye_light": "#cfe9f5",
            "eye_dark": "#5c3a55",


            "blush": {
                "happy": "#f9c2d6", "approval": "#f2b0c8",
                "sleepy": "#eec2d4", "default": "#f4a8c6",
            },


            "states": {


                "idle": "#c2e8d8", "working": "#f6cf9a", "approval": "#ee94ad",
                "happy": "#f2c6e0", "sleepy": "#cfd8f0",
                "annoyed": "#efb49a", "dizzy": "#dcc4f0",
            },
            "fx": ["#f6dfae", "#f2c6e0", "#c2dcf0", "#c2e8d8",
                   "#dcc4f0", "#f4a8c6"],
        },



    },
    "paper": {
        "label": "Paper · Light",

        "background": "space",
        "bg_color": "#fdfaf5",
        "fg_color": "#3b3242",
        "accent_color": "#c2410c",
        "working_color": "#b45309",
        "approval_color": "#be123c",
        "idle_color": "#15803d",
        "tool_color": "#0e7490",
        "tints": {
            "idle": (253, 250, 245), "working": (255, 247, 230),
            "approval": (254, 240, 242), "happy": (255, 244, 250),
            "pixel": (240, 250, 242), "youtube": (254, 238, 238),
            "spotify": (236, 252, 240), "other": (250, 246, 252),
        },


        
        "pet": {
            "ink": "#3b3242",
            "ear_inner": "#f4a3bd",
            "nose": "#ec5f8a",
            "sparkle": "#f5c518",
            "petted": "#e04a7c",
            "tongue": "#e04a7c",
            "eye_light": "#3aa8c4",
            "eye_dark": "#2b2438",
            "blush": {
                "happy": "#f472a0", "approval": "#ee6c96",
                "sleepy": "#f0a0b8", "default": "#f472a0",
            },
            "states": {
                "idle": "#4ade80", "working": "#f59e0b", "approval": "#f43f5e",
                "happy": "#ec4899", "sleepy": "#38bdf8",
                "annoyed": "#fb923c", "dizzy": "#a855f7",
            },
            "fx": ["#f5c518", "#ec4899", "#38bdf8", "#4ade80",
                   "#a855f7", "#f43f5e"],
        },
    },
}

DEFAULT_THEME = "midnight"




THEME_KEYS = (
    "bg_color", "fg_color", "accent_color",
    "working_color", "approval_color", "idle_color", "tool_color",
)

DEFAULT_CONFIG = {
    "width": 760,
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
    "pixel_screensaver_seconds": 0,
    "theme": DEFAULT_THEME,
}


def resolve_theme(name):
    """Return (key, theme_dict). Unknown names fall back to DEFAULT_THEME."""
    if not name:
        name = DEFAULT_THEME
    key = str(name).strip().lower()
    if key not in THEMES:
        key = DEFAULT_THEME
    return key, THEMES[key]


def apply_theme(cfg, name):
    """Write a theme's colours into cfg and return the resolved theme key.

    Mutates cfg in place so callers holding a reference see the change.
    """
    key, theme = resolve_theme(name)
    cfg["theme"] = key
    for k in THEME_KEYS:
        cfg[k] = theme[k]
    return key


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
                raw = json.load(f)
            cfg = {**DEFAULT_CONFIG, **raw}
            
            if "theme" in raw:
                apply_theme(cfg, raw.get("theme"))
            return migrate_config(cfg)
        except Exception:
            pass
    cfg = DEFAULT_CONFIG.copy()
    apply_theme(cfg, DEFAULT_THEME)
    return cfg


def theme_names():
    return list(THEMES.keys())


def theme_label(name):
    key, theme = resolve_theme(name)
    return theme["label"]


def theme_background(name):
    key, theme = resolve_theme(name)
    return theme["background"]


def theme_tints(name):
    key, theme = resolve_theme(name)
    return theme["tints"]




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