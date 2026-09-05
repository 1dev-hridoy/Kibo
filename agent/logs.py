"""
Centralized logging for the Agent — logs all user inputs, AI responses,
tool calls, and errors to terminal with timestamps and colors.
"""

import os
import sys
import time
from datetime import datetime

# ── Colors ─────────────────────────────────────────────────────────────
RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
MAGENTA = "\033[35m"
CYAN = "\033[36m"

# ── Log file setup ─────────────────────────────────────────────────────
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
os.makedirs(LOG_DIR, exist_ok=True)

_log_file = None


def _get_log_file():
    """Get or create today's log file."""
    global _log_file
    today = datetime.now().strftime("%Y-%m-%d")
    path = os.path.join(LOG_DIR, f"agent_{today}.log")
    if _log_file is None or _log_file.name != path:
        if _log_file:
            _log_file.close()
        _log_file = open(path, "a", encoding="utf-8")
    return _log_file


def _ts():
    """Timestamp string."""
    return datetime.now().strftime("%H:%M:%S")


def _write_file(level, source, message):
    """Write to log file."""
    try:
        f = _get_log_file()
        f.write(f"[{_ts()}] [{level}] [{source}] {message}\n")
        f.flush()
    except Exception:
        pass


# ── Public API ─────────────────────────────────────────────────────────

def user_input(source, text):
    """Log a user message from CLI, Web, or Telegram."""
    tag = {"cli": "CLI", "web": "WEB", "telegram": "TG"}.get(source, source.upper())
    print(f"\n{_ts()} {CYAN}{BOLD}[{tag}]{RESET} {BOLD}User:{RESET} {text}")
    _write_file("USER", tag, text)


def ai_response(source, text, tool_calls=None, results=None):
    """Log the AI response and any tool calls."""
    tag = {"cli": "CLI", "web": "WEB", "telegram": "TG"}.get(source, source.upper())
    print(f"{_ts()} {GREEN}{BOLD}[{tag}]{RESET} {GREEN}Agent:{RESET} {text[:200]}{'...' if len(text) > 200 else ''}")

    if tool_calls:
        for tc in tool_calls:
            name = tc.get("name", "?")
            args = tc.get("arguments", {})
            args_str = ", ".join(f"{k}={v!r}" for k, v in args.items()) if args else ""
            print(f"{_ts()} {YELLOW}  -> {name}({args_str}){RESET}")
            _write_file("TOOL_CALL", tag, f"{name}({args_str})")

    if results:
        for r in results:
            r_str = str(r)[:150]
            print(f"{_ts()} {DIM}  <- {r_str}{RESET}")
            _write_file("TOOL_RESULT", tag, r_str)

    _write_file("RESPONSE", tag, text[:500])


def tool_call(source, name, args=None):
    """Log a tool being called."""
    tag = {"cli": "CLI", "web": "WEB", "telegram": "TG"}.get(source, source.upper())
    args_str = ", ".join(f"{k}={v!r}" for k, v in (args or {}).items())
    print(f"{_ts()} {YELLOW}  -> {name}({args_str}){RESET}")
    _write_file("TOOL_CALL", tag, f"{name}({args_str})")


def tool_result(source, name, result):
    """Log a tool result."""
    tag = {"cli": "CLI", "web": "WEB", "telegram": "TG"}.get(source, source.upper())
    r_str = str(result)[:200]
    print(f"{_ts()} {DIM}  <- {name}: {r_str}{RESET}")
    _write_file("TOOL_RESULT", tag, f"{name}: {r_str}")


def error(source, message):
    """Log an error."""
    tag = {"cli": "CLI", "web": "WEB", "telegram": "TG"}.get(source, source.upper())
    print(f"{_ts()} {RED}{BOLD}[{tag}] ERROR:{RESET} {message}")
    _write_file("ERROR", tag, message)


def info(message):
    """Log general info."""
    print(f"{_ts()} {DIM}{message}{RESET}")
    _write_file("INFO", "SYS", message)


def startup(mode, details=""):
    """Log bot/server startup."""
    print(f"\n{CYAN}{'='*60}{RESET}")
    print(f"{CYAN}{BOLD}  Agent — {mode} mode{RESET}")
    if details:
        print(f"{DIM}  {details}{RESET}")
    print(f"{CYAN}{'='*60}{RESET}\n")
    _write_file("STARTUP", "SYS", f"{mode}: {details}")


def shutdown():
    """Log shutdown and close log file."""
    global _log_file
    print(f"\n{_ts()} {YELLOW}Agent shutting down.{RESET}")
    _write_file("SHUTDOWN", "SYS", "Agent stopped")
    if _log_file:
        _log_file.close()
        _log_file = None
