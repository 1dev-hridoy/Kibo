"""
Telegram access control — only allowed chats can drive this PC.
Ids come from AGENT_TELEGRAM_ALLOWED_CHATS (comma list), the owner
(auto-claimed on first contact), a trusted group, or /allow <chat_id>.
"""

import json
import os

_ALLOW_FILE = os.path.expanduser("~/.config/kibo/telegram_allowed.json")


def _env_ids():
    raw = os.environ.get("AGENT_TELEGRAM_ALLOWED_CHATS", "")
    ids = set()
    for part in raw.split(","):
        part = part.strip()
        if part.lstrip("-").isdigit():
            ids.add(int(part))
    return ids


def _load():
    try:
        with open(_ALLOW_FILE) as f:
            data = json.load(f)
        return set(int(x) for x in data.get("chats", []))
    except (ValueError, OSError, AttributeError):
        pass
    old = os.path.expanduser("~/.config/kibo/telegram_owner")
    try:
        with open(old) as f:
            return {int(f.read().strip())}
    except (ValueError, OSError):
        return set()


def _save(ids):
    try:
        os.makedirs(os.path.dirname(_ALLOW_FILE), exist_ok=True)
        with open(_ALLOW_FILE, "w") as f:
            json.dump({"chats": sorted(ids)}, f, indent=2)
    except OSError:
        pass


def allowed_ids():
    return _env_ids() | _load()


def add_allowed(chat_id):
    ids = _load()
    ids.add(int(chat_id))
    _save(ids)
    return sorted(ids)


def is_allowed(chat_id) -> bool:
    ids = allowed_ids()
    if chat_id in ids:
        return True
    if not ids:
        add_allowed(chat_id)
        try:
            print(f"[Telegram] First contact — chat {chat_id} registered as owner.")
        except Exception:
            pass
        return True
    return False


def owner_ids():
    return _load()
