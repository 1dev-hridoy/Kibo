"""
Simple web authentication.
"""

import os
import secrets
import hashlib
import time

AUTH_FILE = os.path.expanduser("~/.kibo_web_auth.json")
DEFAULT_PASSWORD = "kibo"
_token = None
_token_expiry = None


def _load_auth():
    """Load auth config from disk."""
    import json
    if os.path.exists(AUTH_FILE):
        with open(AUTH_FILE) as f:
            return json.load(f)
    return {}


def setup_password(password):
    """Set or change the web UI password."""
    import json
    salt = secrets.token_hex(16)
    hashed = hashlib.pbkdf2_hmac(
        "sha256", password.encode(), salt.encode(), 100000
    ).hex()
    config = {"salt": salt, "hash": hashed}
    with open(AUTH_FILE, "w") as f:
        json.dump(config, f)
    return "Password set successfully"


def verify_password(password):
    """Verify a password against the stored hash."""
    config = _load_auth()
    if not config:
    
        return password == DEFAULT_PASSWORD
    hashed = hashlib.pbkdf2_hmac(
        "sha256", password.encode(), config["salt"].encode(), 100000
    ).hex()
    return hashed == config["hash"]


def generate_token():
    """Generate a session token (valid for 24 hours)."""
    global _token, _token_expiry
    _token = secrets.token_urlsafe(32)
    _token_expiry = time.time() + 86400  
    return _token


def verify_token(token):
    """Verify a session token."""
    if not token or not _token or not _token_expiry:
        return False
    if time.time() > _token_expiry:
        return False
    return secrets.compare_digest(str(token), str(_token))


def is_auth_required():
    """Check if auth is required."""
    return True 


def remove_password():
    """Remove password protection."""
    if os.path.exists(AUTH_FILE):
        os.remove(AUTH_FILE)
        return "Password removed"
    return "No password was set"
