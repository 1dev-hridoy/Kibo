"""
Typo correction and fuzzy matching for user input.
Fixes common typos and matches app names phonetically.
"""

import re
import os
import shutil


TYPO_MAP = {
   
    "opem": "open", "opne": "open", "opn": "open",
    "volme": "volume", "volmue": "volume", "vlume": "volume", "volu": "volume",
    "screnshot": "screenshot", "screenhot": "screenshot", "screeshot": "screenshot",
    "brighness": "brightness", "brightnes": "brightness", "brighetness": "brightness",
    "batery": "battery", "battrey": "battery", "batttery": "battery",
    "proccess": "process", "proces": "process", "prccess": "process",
    "processes": "processes", "proccesses": "processes",
    "temprature": "temperature", "temperatur": "temperature", "tempreature": "temperature",
    "wificonnection": "wifi connection", "wifii": "wifi",
    "netwrok": "network", "newtork": "network", "netowrk": "network",
    "interent": "internet", "intenet": "internet", "internetconnection": "internet connection",
    "downlaod": "download", "donwload": "download", "dwonload": "download",
    "termnal": "terminal", "temrinal": "terminal", "terminl": "terminal",
    "calulator": "calculator", "caluclator": "calculator", "claculator": "calculator",
    "notepad": "notepad", "ntepad": "notepad", "noteapd": "notepad",
    "browswer": "browser", "browsr": "browser",
    "settigns": "settings", "setings": "settings", "settins": "settings",
    "chekc": "check", "chek": "check",
    "infromation": "information", "infomation": "information",
    "runing": "running", "runnig": "running",
    "instal": "install", "instalation": "installation",
    "uninstal": "uninstall",
    "delet": "delete", "deleet": "delete",
    "creat": "create", "craete": "create",
    "mvoe": "move", "moev": "move",
    "coppy": "copy", "coy": "copy",
    "past": "paste", "pste": "paste",
    "loock": "lock", "lok": "lock",
    "shutdwon": "shutdown", "shutdonw": "shutdown",
    "restatr": "restart", "resart": "restart",
    "brwose": "browse", "broswe": "browse",
    "musci": "music", "msuic": "music",
    "vidoe": "video", "vdieo": "video",
    "pciture": "picture", "picutre": "picture",
    "fodler": "folder", "foler": "folder",
    "direcotry": "directory", "directroy": "directory",
    "mesage": "message", "messge": "message",
    "ntofication": "notification", "notifcation": "notification",
    "brighjt": "brightness",
    "speker": "speaker", "spaker": "speaker",
    "micorphone": "microphone", "microhpone": "microphone",
    "cmaera": "camera", "camrea": "camera",
    "reocrd": "record", "recrod": "record",
    "plau": "play", "palys": "plays",
    "storp": "stop", "stoped": "stopped",
    "pushe": "push", "pusdh": "push",
    "clsoe": "close", "clos": "close",
    "minmize": "minimize", "minimze": "minimize",
    "maximze": "maximize", "maxmize": "maximize",
    "foucs": "focus", "fcous": "focus",
    "tyep": "type", "tpye": "type",
    "pres": "press", "prss": "press",
    "sclaing": "scaling", "scalng": "scaling",
    "repo": "repository", "repositry": "repository",
    "commadn": "command", "comand": "command", "cmmand": "command",
    "pakcage": "package", "pakage": "package", "packge": "package",
    "modle": "model", "moel": "model",
    "soruce": "source", "soruc": "source",
    "brnach": "branch", "brnch": "branch",
    "cmmit": "commit", "comit": "commit",
    "pussh": "push", "pushh": "push",
    "plul": "pull", "pulll": "pull",
    "clne": "clone", "clon": "clone",
    "syncc": "sync", "syncy": "sync",
    "lanch": "launch", "lounch": "launch",
    "srevice": "service", "servce": "service",
    "procss": "process", "porcess": "process",
    "daemn": "daemon", "dameon": "daemon",
    "cotext": "context", "contex": "context",
    "histroy": "history", "hsitory": "history",
    "remeber": "remember", "remmber": "remember",
    "forgrt": "forget", "forgtet": "forget",
    "exlpain": "explain", "explan": "explain",
    "anaylze": "analyze", "analyez": "analyze",
    "currnet": "current", "curent": "current",
    "avaialble": "available", "avaiable": "available",
    "specfic": "specific", "speciifc": "specific",
    "aplication": "application", "applcation": "application",
    "funciton": "function", "fucntion": "function",
    "arguement": "argument", "arguemnt": "argument",
    "paramter": "parameter", "paramater": "parameter",
    "reponse": "response", "respone": "response",
    "reqeust": "request", "reuqest": "request",
    "sequnce": "sequence", "seqence": "sequence",
    "vaiable": "variable", "varialbe": "variable",
    "strnig": "string", "stirng": "string",
    "numbre": "number", "nuber": "number",
    "boolen": "boolean", "bolean": "boolean",
    "arrary": "array", "arrray": "array",
    "dictonary": "dictionary", "dictionay": "dictionary",
    "lsit": "list", "liist": "list",
    "tuople": "tuple", "tupel": "tuple",
    "clss": "class", "calss": "class",
    "methd": "method", "metohd": "method",
    "moudle": "module", "moduel": "module",
    "packge": "package", "pakcage": "package",
    "libary": "library", "librray": "library",
    "framwork": "framework", "framewrok": "framework",
    "dtabase": "database", "datbase": "database",
    "qry": "query", "qeury": "query",
    "indxe": "index", "idnex": "index",
    "colmn": "column", "colum": "column",
    "taable": "table", "tabl": "table",
    "rle": "role", "rol": "role",
    "usre": "user", "usr": "user",
    "admimn": "admin", "admn": "admin",
    "pssword": "password", "pasword": "password",
    "emial": "email", "email": "email",
    "liunx": "linux", "lniux": "linux",
    "ubntu": "ubuntu", "ubutnu": "ubuntu",
    "archh": "arch", "arhc": "arch",
    "fedor": "fedora", "fedpra": "fedora",
    "deiban": "debian", "debin": "debian",
    "cnetos": "centos", "centso": "centos",
    "manjro": "manjaro", "manjaro": "manjaro",
    "popos": "pop os", "pop_os": "pop os",
    "mintt": "mint", "linxu mint": "linux mint",
    "kubntu": "kubuntu", "xubntu": "xubuntu",
    "lubntu": "lubuntu",
    "gnme": "gnome", "gnom": "gnome",
    "kdeee": "kde", "kdd": "kde",
    "xfce": "xfce", "xfce4": "xfce4",
    "cinnamon": "cinnamon", "mateee": "mate",
    "budgie": "budgie", "deepin": "deepin",
    "hyprland": "hyprland", "swayyy": "sway",
    "i3wm": "i3", "i3gg": "i3",
    "bspwm": "bspwm", "dwm": "dwm",
    "qtile": "qtile", "awesome": "awesome",
    "xorg": "xorg", "wayland": "wayland",
    "nviida": "nvidia", "nvidai": "nvidia",
    "amdnd": "amd", "amdd": "amd",
    "inteel": "intel", "intle": "intel",
    "bluetooh": "bluetooth", "bluethooth": "bluetooth",
    "usbb": "usb", "ubs": "usb",
    "hdmi": "hdmi", "dp": "displayport",
    "ethrenet": "ethernet", "etherent": "ethernet",
    "wiffi": "wifi", "wiifi": "wifi",
    "ssd": "ssd", "hd": "hard drive",
    "ram": "ram", "cpu": "cpu",
    "gpuy": "gpu", "gpyu": "gpu",
    "momery": "memory", "memroy": "memory",
    "dsk": "disk", "dsik": "disk",
    "frie": "fire", "firee": "fire",
    "foxe": "fox", "foxfire": "firefox",
    "chrme": "chrome", "googl chrome": "google chrome",
    "edeg": "edge", "msedge": "edge",
    "safri": "safari", "safrai": "safari",
    "oper": "opera", "oprea": "opera",
    "vivald": "vivaldi", "vivaldi": "vivaldi",
    "braev": "brave", "brav": "brave",
    "dscord": "discord", "disord": "discord",
    "slcak": "slack", "salc": "slack",
    "teh": "the", "taht": "that",
    "wiht": "with", "wtih": "with",
    "frmo": "from", "form": "from",
    "abotu": "about", "abut": "about",
    "shoud": "should", "shuold": "should",
    "woudl": "would", "woldu": "would",
    "coudl": "could", "cuold": "could",
    "wil l": "will", "wi ll": "will",
    "maek": "make", "mkae": "make",
    "hwo": "how", "hw": "how",
    "wha t": "what", "whet": "what",
    "whic h": "which", "whihc": "which",
    "whe re": "where", "whre": "where",
    "whe n": "when", "wen": "when",
    "wh y": "why", "whiy": "why",
    "botu": "both", "btoh": "both",
    "afer": "after", "afetr": "after",
    "beofre": "before", "befor": "before",
    "beetwen": "between", "bewteen": "between",
    "ithin": "within", "wihtin": "within",
    "withotu": "without", "witohut": "without",
    "agian": "again", "agianst": "against",
    "becuase": "because", "becasue": "because",
    "alhtough": "although", "althogh": "although",
    "howevr": "however", "hwoever": "however",
    "therfore": "therefore", "therefor": "therefore",
    "moerover": "moreover", "morever": "moreover",
    "furthermroe": "furthermore", "futhermore": "furthermore",
    "nevetheless": "nevertheless", "neverthless": "nevertheless",
    "nonethless": "nonetheless", "nontheless": "nonetheless",
    "consequnetly": "consequently", "conseqently": "consequently",
    "similiarly": "similarly", "simlarly": "similarly",
    "alternativley": "alternatively", "alternatvely": "alternatively",
    "addtionally": "additionally", "addtitionally": "additionally",
    "moreoever": "moreover", "mroeover": "moreover",
    "futhrer": "further", "futhter": "further",
    "adn": "and", "nad": "and",
    "ot": "to", "t o": "to",
    "fo": "of", "o f": "of",
    "in ": " in ", "ni": "in",
    "si": "is", "i s": "is",
    "it ": " it ", "ti": "it",
    "on ": " on ", "no": "on",
    "at ": " at ", "ta": "at",
    "or ": " or ", "ro": "or",
    "if ": " if ", "fi": "if",
    "do ": " do ", "od": "do",
    "so ": " so ", "os": "so",
    "up ": " up ", "pu": "up",
    "go ": " go ", "og": "go",
}

# ── Phonetic / soundex matching ──────────────────────────────────────
def _soundex(name):
    """Simple soundex for fuzzy app name matching."""
    name = name.lower().strip()
    if not name:
        return ""
    soundex = name[0].upper()
    code_map = {
        'b': '1', 'f': '1', 'p': '1', 'v': '1',
        'c': '2', 'g': '2', 'j': '2', 'k': '2', 'q': '2', 's': '2', 'x': '2', 'z': '2',
        'd': '3', 't': '3',
        'l': '4',
        'm': '5', 'n': '5',
        'r': '6',
    }
    prev = code_map.get(name[0], '0')
    for char in name[1:]:
        code = code_map.get(char, '0')
        if code != '0' and code != prev:
            soundex += code
        prev = code
    return (soundex + '000')[:4]


def _levenshtein(s1, s2):
    """Levenshtein distance between two strings."""
    if len(s1) < len(s2):
        return _levenshtein(s2, s1)
    if len(s2) == 0:
        return len(s1)
    prev_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        curr_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = prev_row[j + 1] + 1
            deletions = curr_row[j] + 1
            substitutions = prev_row[j] + (c1 != c2)
            curr_row.append(min(insertions, deletions, substitutions))
        prev_row = curr_row
    return prev_row[-1]


# ── Known app names (for fuzzy matching) ─────────────────────────────
KNOWN_APPS = [
    # Browsers
    "firefox", "chrome", "google-chrome", "brave", "brave-browser",
    "opera", "vivaldi", "edge", "msedge", "safari", "chromium",
    # Dev tools
    "code", "vscode", "visual-studio-code", "sublime-text", "atom",
    "vim", "nvim", "nano", "emacs", "helix", "kakoune",
    "intellij", "idea", "pycharm", "webstorm", "android-studio",
    "postman", "insomnia", "thunder-client",
    # Communication
    "discord", "slack", "teams", "zoom", "skype", "telegram-desktop",
    "signal", "whatsapp-desktop", "thunderbird",
    # Media
    "vlc", "mpv", "obs-studio", "obs", "audacity", "gimp", "inkscape",
    "blender", "krita", "shotwell", "eog", "feh", "sxiv", "nsxiv",
    "rhythmbox", "spotify", "cmus", "playerctl",
    # System
    "nautilus", "dolphin", "thunar", "pcmanfm", "nemo", "doublecmd",
    "gnome-terminal", "kitty", "alacritty", "wezterm", "tilix", "konsole",
    " xfce4-terminal", "lxterminal", "mate-terminal", "terminology",
    "htop", "btop", "bashtop", "glances", "nmon", "iotop",
    "gnome-system-monitor", "ksystemlog", "journalctl",
    # Office
    "libreoffice", "libreoffice-writer", "libreoffice-calc", "libreoffice-impress",
    "evince", "okular", "zathura", "calibre", "pandoc",
    # Graphics
    "blender", "freecad", "openscad", "meshlab",
    # Gaming
    "steam", "lutris", "heroic", "mangohud", "gamemode",
    # Other
    "filezilla", "gparted", "timeshift", "clonezilla",
    "veracrypt", "keepassxc", "bitwarden", "1password",
    "obsidian", "notion", "logseq", "joplin",
]


def correct_typos(text):
    """Fix common typos in user input."""
    words = text.lower().split()
    corrected = []
    for word in words:
        clean = re.sub(r'[^\w]', '', word)
        if clean in TYPO_MAP:
            corrected.append(TYPO_MAP[clean])
        else:
            corrected.append(word)
    return " ".join(corrected)


def fuzzy_find_app(name, app_map=None, url_map=None):
    """Find the best matching app name using fuzzy matching.

    Args:
        name: The app name to search for
        app_map: Dict of app names to commands (LINUX_APPS, etc.)
        url_map: Dict of app names to URLs (APP_URLS)

    Returns:
        The best matching name, or None if no match
    """
    name_lower = name.lower().strip()
    candidates = {}

    if app_map:
        candidates.update(app_map)
    if url_map:
        candidates.update(url_map)

    if not candidates:
        return None

    # Exact match
    if name_lower in candidates:
        return name_lower

    # Substring match (require at least 3 chars to avoid false positives)
    for key in candidates:
        if len(key) >= 3 and (name_lower in key or key in name_lower):
            return key

    # Levenshtein distance (allow 1-2 edits based on length)
    best_match = None
    best_dist = float('inf')
    max_dist = max(1, len(name_lower) // 3)

    # Skip very short candidates (like "x") unless name is also short
    # Also skip candidates that are much shorter than the input
    for key in candidates:
        if len(key) < 3 and len(name_lower) > 4:
            continue
        if len(key) < len(name_lower) // 2:
            continue
        dist = _levenshtein(name_lower, key)
        if dist < best_dist and dist <= max_dist:
            best_dist = dist
            best_match = key

    if best_match:
        return best_match

    # Soundex match
    name_soundex = _soundex(name_lower)
    for key in candidates:
        if len(key) >= 3 and _soundex(key) == name_soundex:
            return key

    return None


def find_command_for_app(name):
    """Universal app finder — tries multiple strategies to find and return
    the command to launch an app.

    Returns:
        (command_list, source) or (None, None) if not found
    """
    from agent.config_apps import LINUX_APPS, APP_URLS, WINDOWS_APPS, MACOS_APPS
    from agent.config import IS_LINUX, IS_WINDOWS, IS_MACOS

    name_lower = name.lower().strip()

    # 1. Check OS-specific app map
    if IS_LINUX:
        apps = LINUX_APPS
    elif IS_WINDOWS:
        apps = WINDOWS_APPS
    elif IS_MACOS:
        apps = MACOS_APPS
    else:
        apps = {}

    # Try fuzzy match in app map
    match = fuzzy_find_app(name_lower, app_map=apps)
    if match:
        return apps[match], "app_map"

    # 2. Check URL map
    match = fuzzy_find_app(name_lower, url_map=APP_URLS)
    if match:
        return [APP_URLS[match]], "url_map"

    # 3. Try `which` command (Linux/macOS)
    if IS_LINUX or IS_MACOS:
        result = shutil.which(name_lower)
        if result:
            return [result], "which"

        # Try common binary name patterns
        for prefix in ["", "google-", "brave-", "firefox-"]:
            for suffix in ["", "-browser", "-bin"]:
                candidate = f"{prefix}{name_lower}{suffix}"
                result = shutil.which(candidate)
                if result:
                    return [result], "which"

    # 4. Try checking if it's a running process and get its command
    if IS_LINUX:
        try:
            import subprocess
            result = subprocess.run(
                ["pgrep", "-a", name_lower],
                capture_output=True, text=True, timeout=3
            )
            if result.returncode == 0 and result.stdout.strip():
                # Parse the first matching process
                line = result.stdout.strip().split("\n")[0]
                parts = line.split(None, 1)
                if len(parts) > 1:
                    # Extract the command from ps output
                    cmd = parts[1].split()[0] if parts[1].split() else None
                    if cmd:
                        return [cmd], "process"
        except Exception:
            pass

    # 5. Last resort — treat as URL if it contains a dot
    if "." in name_lower and " " not in name_lower:
        url = name_lower if name_lower.startswith("http") else f"https://{name_lower}"
        return [url], "url"

    return None, None
