import os
import shutil
import subprocess
import threading
import urllib.request

SOUND_DIR = os.path.expanduser("~/.config/kibo/sounds")

UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64)"}

SOUNDS = {
    "water": [
        "https://assets.mixkit.co/active_storage/sfx/1180/1180-preview.mp3",
    ],
    "grass": [
        "https://assets.mixkit.co/active_storage/sfx/2390/2390-preview.mp3",
    ],
    "stretch": [
        "https://assets.mixkit.co/active_storage/sfx/2310/2310-preview.mp3",
    ],
    "eyes": [
        "https://assets.mixkit.co/active_storage/sfx/2317/2317-preview.mp3",
    ],
    "posture": [
        "https://assets.mixkit.co/active_storage/sfx/2320/2320-preview.mp3",
    ],
}




def ensure_sound(name):
    path = os.path.join(SOUND_DIR, f"{name}.mp3")
    if os.path.exists(path) and os.path.getsize(path) > 10240:
        return path
    for url in SOUNDS.get(name, []):
        try:
            os.makedirs(SOUND_DIR, exist_ok=True)
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=30) as r:
                data = r.read()
            if len(data) > 10240:
                tmp = path + ".tmp"
                with open(tmp, "wb") as f:
                    f.write(data)
                os.replace(tmp, path)
                return path
        except Exception:
            continue
    return ""





def _play_sync(name):
    path = ensure_sound(name)
    if not path:
        return
    for player, args in (
        ("mpg123", ["-q", path]),
        ("mpv", ["--no-video", "--really-quiet", path]),
        ("ffplay", ["-nodisp", "-autoexit", "-loglevel", "quiet", path]),
        ("play", ["-q", path]),
    ):
        if shutil.which(player):
            try:
                subprocess.run([player] + args,
                               stdout=subprocess.DEVNULL,
                               stderr=subprocess.DEVNULL, timeout=15)
                return
            except Exception:
                continue



def play_sound(name):
    threading.Thread(target=_play_sync, args=(name,), daemon=True).start()
