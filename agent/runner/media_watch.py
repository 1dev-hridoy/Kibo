"""
Media playback watcher — detects what is playing on this PC and
publishes it for the desktop widget.

Covers:
  • Spotify desktop app   (MPRIS: org.mpris.MediaPlayer2.spotify)
  • Spotify web / YouTube in Chrome, Edge or Firefox
                           (MPRIS instances exposed by the browser)
  • anything else MPRIS exposes (VLC, mpv, Rhythmbox, …)

Detection prefers D-Bus directly (dbus-python), then falls back to the
`playerctl` command-line tool. Nothing is written when no media session is
playing, so the widget knows to drop the music theme.

Output: ~/.config/kibo/media_state.json
  {"playing": true, "source": "spotify"|"youtube"|...,
   "title": "...", "artist": "...", "track_key": "..."}
"""

import json
import os
import re
import shutil
import subprocess
import threading
import time



STATE_FILE = os.path.expanduser("~/.config/kibo/media_state.json")

MPRIS_RE = re.compile(r"^org\.mpris\.MediaPlayer2\.(.+)$")

SPOTIFY_NAMES = ("spotify",)
YOUTUBE_HOSTS = ("youtube.com", "www.youtube.com", "music.youtube.com",
                 "youtu.be", "youtube-nocookie.com")

YOUTUBE_WORDS = ("youtube", "official video", "official audio",
                 "official song", "(official)", "[official]",
                 "official)", "official visualizer", "music video",
                 "lyric video", "lyrics", "audio only", "hd", "1080p",
                 "4k", "full hd", "lytics", "ringtone", "trending",
                 "episode", "web series", "trailer", "lyrical",
                 "visualizer", "cover", "remix", "live session")
MUSIC_WORDS = ("spotify", "soundcloud", "bandcamp", "apple music",
               "amazon music", "deezer", "tidal", "pandora", "mixcloud")




def _norm(text):
    return re.sub(r"\s+", " ", (text or "").strip()).lower()


def _track_key(meta):
    title = meta.get("title") or meta.get("xesam:title") or ""
    artist = meta.get("artist") or meta.get("xesam:artist") or ""
    if isinstance(artist, list):
        artist = " ".join(str(a) for a in artist)
    url = meta.get("url") or meta.get("xesam:url") or meta.get("location") or ""
    raw = _norm(title + " " + artist) or _norm(url)
    return raw




BROWSER_NAMES = ("brave", "chrome", "chromium", "firefox", "edge", "vivaldi",
                "opera", "brave-beta")





DEFAULT_BROWSER_SOURCE = os.environ.get("KIBO_MEDIA_BROWSER_SOURCE",
                                        "youtube").strip().lower()


def _source_from(name, meta):
    name = _norm(name)
    url = _norm(meta.get("url") or meta.get("xesam:url")
                or meta.get("location") or "")
    track_id = _norm(meta.get("trackid") or meta.get("mpris:trackid")
                     or meta.get("mpris:trackid") or "")
    title = _norm(meta.get("title") or meta.get("xesam:title") or "")
    artist = _norm(meta.get("artist") or meta.get("xesam:artist") or "")
    haystack = f"{url} {track_id} {title} {artist}"



    for host in YOUTUBE_HOSTS:
        if host in haystack:
            return "youtube"
    if "spotify" in haystack or "spotify" in name:
        return "spotify"

    
    if any(w in haystack for w in MUSIC_WORDS):
        return "spotify"
    if any(w in haystack for w in YOUTUBE_WORDS):
        return "youtube"
    if any(b in name for b in BROWSER_NAMES):
        return DEFAULT_BROWSER_SOURCE if DEFAULT_BROWSER_SOURCE in (
            "youtube", "spotify") else "youtube"
    return "other"





def _pick_player(players):
    if not players:
        return None
    playing = [p for p in players
               if str(p.get("status", "")).lower() == "playing"]
    pool = playing or players
    for pref in SPOTIFY_NAMES:
        for p in pool:
            if pref in _norm(p.get("name", "")):
                return p
    return pool[0]


def _dbus_probe():
    try:
        import dbus
    except ImportError:
        return None
    try:
        bus = dbus.SessionBus()
    except Exception:
        return None
    try:
        names = [str(n) for n in bus.list_names()
                 if str(n).startswith("org.mpris.MediaPlayer2.")]
    except Exception:
        return None
    out = []



    for name in names:
        m = MPRIS_RE.match(name)
        if not m:
            continue
        try:
            proxy = bus.get_object(name, "/org/mpris/MediaPlayer2")
            props = dbus.Interface(proxy, "org.freedesktop.DBus.Properties")
            status = str(props.Get("org.mpris.MediaPlayer2.Player",
                                    "PlaybackStatus")).lower()
            meta_raw = props.Get("org.mpris.MediaPlayer2.Player", "Metadata")
            meta = {}


            for k, v in meta_raw.items():

                key = str(k).split(":")[-1]
                if isinstance(v, dbus.Array):
                    vals = [str(x) for x in v]
                    meta[key] = vals[0] if len(vals) == 1 else vals
                else:



                    meta[key] = str(v)
            meta["mpris:trackid"] = meta.get("trackid", "")
            identity = str(props.Get("org.mpris.MediaPlayer2", "Identity"))
            desktop = str(props.Get("org.mpris.MediaPlayer2", "DesktopEntry"))
            out.append({"name": identity or desktop or m.group(1),
                        "status": status, "meta": meta})
        except Exception:
            continue
    return out or None




def _playerctl_probe():
    if not shutil.which("playerctl"):
        return None
    players = []


    try:
        meta_out = subprocess.run(
            ["playerctl", "-a", "metadata", "--format",
             "{{playerName}}|{{status}}|{{title}}|{{artist}}|{{xesam:url}}"
             "|{{mpris:trackid}}"],
            capture_output=True, text=True, timeout=5).stdout
    except Exception:


        return None

    
    for line in meta_out.splitlines():
        parts = line.split("|")
        if len(parts) < 3:
            continue
        name, status = parts[0], parts[1].lower()
        title = parts[2] if len(parts) > 2 else ""
        artist = parts[3] if len(parts) > 3 else ""
        url = parts[4] if len(parts) > 4 else ""
        trackid = parts[5] if len(parts) > 5 else ""
        players.append({"name": name, "status": status,
                        "meta": {"title": title, "artist": artist,
                                 "url": url, "mpris:trackid": trackid}})
    return players or None


def _read_state():
    try:
        with open(STATE_FILE) as f:
            data = json.load(f)
        if isinstance(data, dict):
            return data
    except (OSError, ValueError):
        pass
    return None


def _write_state(data):
    try:
        os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
        tmp = STATE_FILE + ".tmp"
        with open(tmp, "w") as f:
            json.dump(data, f, indent=2)
        os.replace(tmp, STATE_FILE)
    except OSError:
        pass


def scan():
    """Return the media state dict, or None when nothing is playing."""
    players = _dbus_probe() or _playerctl_probe()
    if not players:
        return None
    player = _pick_player(players)


    if not player:
        return None
    if str(player.get("status", "")).lower() != "playing":
        return None
    meta = player.get("meta", {})


    title = meta.get("title") or meta.get("xesam:title") or ""
    if isinstance(title, list):
        title = title[0] if title else ""
    artist = meta.get("artist") or meta.get("xesam:artist") or ""
    if isinstance(artist, list):


        artist = artist[0] if artist else ""
    key = _track_key(meta)
    if not title and not artist:
        return None
    return {
        "playing": True,
        "source": _source_from(player.get("name", ""), meta),
        "title": title or "",
        "artist": artist or "",
        "track_key": key,
        "ts": time.time(),
    }


def start_watcher(interval=2.0):
    """Background thread keeping ~/.config/kibo/media_state.json fresh."""
    if interval <= 0:
        return None

    def loop():

        last_key = None
        last_playing = None
        while True:


            try:
                state = scan()
                key = state.get("track_key") if state else None
                playing = bool(state and state.get("playing"))
                if (key != last_key or playing != last_playing):
                    _write_state(state or {"playing": False})
                    last_key = key
                    last_playing = playing
            except Exception:
                pass
            time.sleep(interval)

            

    t = threading.Thread(target=loop, daemon=True)
    t.start()
    return t


def current():
    """Last written state, or a synthetic stopped state."""
    state = _read_state()
    if state and state.get("playing"):
        return state
    return {"playing": False}
