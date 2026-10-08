"""
Unified entry point for the Agent.

Usage:
  python -m agent                 # Interactive CLI
  python -m agent web             # Web UI (browser)
  python -m agent web --port 8080 # Custom port
  python -m agent telegram        # Telegram bot
  python -m agent all             # Web + Telegram
"""

import sys
import os

from .config import TELEGRAM_TOKEN, WEB_PORT


_PROMPTED_FLAG = os.path.expanduser("~/.config/kibo/autostart_prompted")


def _maybe_prompt_autostart():
    try:
        if os.path.exists(_PROMPTED_FLAG):
            return
        if not sys.stdin.isatty():
            return
        os.makedirs(os.path.dirname(_PROMPTED_FLAG), exist_ok=True)
        ans = input("Start Kibo automatically when this PC starts? [y/N]: ").strip().lower()
        open(_PROMPTED_FLAG, "w").write(ans or "n")
        if ans in ("y", "yes"):
            from agent.runner.autostart import enable
            print(enable())
        else:
            print("OK - Kibo will not autostart. You can change this anytime by asking me.")
    except Exception:
        pass


def _maybe_start_widget(args):
    """Spawn the desktop widget as its own process so it shows in every
    mode (cli/web/telegram/all). Returns True if spawned."""
    if "--no-widget" in args:
        return False

    
    try:
        import tkinter  # noqa: F401
    except ImportError:
        return False

    
    if os.name == "posix" and not os.environ.get("DISPLAY"):
        print("[Widget] No display found — widget needs a desktop session.")
        return False
    try:

        import subprocess
        kwargs = {"stdout": subprocess.DEVNULL, "stderr": subprocess.DEVNULL}
        if os.name == "posix":
            kwargs["start_new_session"] = True
        else:
            kwargs["creationflags"] = getattr(subprocess, "DETACHED_PROCESS", 0)
        subprocess.Popen([sys.executable, "-m", "agent.desktop_widget"], **kwargs)
        print("[Widget] Desktop widget started.")
        return True
    except Exception as e:
        print(f"[Widget] Could not start desktop widget: {e}")
        return False





def _setup_telegram_first_run():
    """First-time telegram setup: ask for bot token, group chat id and
    owner user id. Returns the token (or empty string)."""
    from .config import TELEGRAM_TOKEN
    token = TELEGRAM_TOKEN if ":" in (TELEGRAM_TOKEN or "") else ""
    if not token and sys.stdin.isatty():
        print("Telegram setup — create a bot with @BotFather to get a token.")
        for _ in range(3):


            token = input("Bot token: ").strip()
            if token and ":" in token:
                break
            print("That doesn't look like a bot token (format 123:ABC). Try again.")
       
       
        else:

            return ""
        try:
            env_path = os.path.join(os.path.dirname(os.path.dirname(
                os.path.abspath(__file__))), ".env")
            lines = []
            if os.path.exists(env_path):
                with open(env_path) as f:
                    lines = [l for l in f.read().splitlines()
                             if not l.startswith("AGENT_TELEGRAM_TOKEN=")]
            lines.append(f"AGENT_TELEGRAM_TOKEN={token}")
            with open(env_path, "w") as f:
                f.write("\n".join(lines) + "\n")


            print(f"Token saved to {env_path}")
        except OSError as e:
            print(f"Could not save token: {e}")
    if token and sys.stdin.isatty():
        from agent.telegram.auth import allowed_ids, add_allowed
        if not allowed_ids():

            group = input("Group chat id (Enter to skip): ").strip()
            if group.lstrip("-").isdigit():
                add_allowed(int(group))
                print(f"Group {group} allowed.")
            user = input("Your user id (/chatid in the bot, Enter to skip): ").strip()
            if user.lstrip("-").isdigit():
                add_allowed(int(user))
                print(f"User {user} allowed.")

                
            if not group and not user:
                print("Skipped — the first chat to message the bot becomes owner.")
    return token


def main():
    args = sys.argv[1:]
    mode = args[0].lower() if args else "cli"

    _maybe_prompt_autostart()

    if mode == "web":
        from agent.web import start_web
        port = int(args[1]) if len(args) > 1 and args[1].isdigit() else WEB_PORT
        if "--telegram" in args:
            tidx = args.index("--telegram") + 1
            token = args[tidx] if tidx < len(args) else TELEGRAM_TOKEN
            if token:
                from agent.telegram import start_telegram
                start_telegram(token)



       
        if "--no-widget" not in args:
            try:
                import tkinter  
                import threading
                from agent.web.app import app, socketio
                from agent.config import WEB_HOST, WEB_SSL, SSL_CERT, SSL_KEY
                import os


             
                def _run_web():
                    ssl_context = None
                    if WEB_SSL and os.path.exists(SSL_CERT) and os.path.exists(SSL_KEY):
                        ssl_context = (SSL_CERT, SSL_KEY)
                    print(f"Kibo Web UI: http{'s' if ssl_context else ''}://{WEB_HOST}:{port}")
                    socketio.run(app, host=WEB_HOST, port=port, debug=False,
                                 allow_unsafe_werkzeug=True, ssl_context=ssl_context)

                web_thread = threading.Thread(target=_run_web, daemon=True)
                web_thread.start()


               
                from agent.desktop_widget import KiboWidget
                KiboWidget().run()
                return
            except ImportError:
                pass
            except Exception as e:
                print(f"[Widget] Could not start desktop widget: {e}")

        start_web(port=port)

    elif mode == "telegram":
        token = args[1] if len(args) > 1 else TELEGRAM_TOKEN
        if not token or ":" not in token:
            token = _setup_telegram_first_run() if len(args) <= 1 else ""
        if not token or ":" not in token:
            print("Error: Provide Telegram bot token.")
            print("Usage: python -m agent telegram YOUR_BOT_TOKEN")
            print("Or set AGENT_TELEGRAM_TOKEN env var.")
            sys.exit(1)
        from agent.telegram import start_telegram
        start_telegram(token)
        _maybe_start_widget(args)
        import time
        while True:
            time.sleep(60)

    elif mode == "all":
        from agent.web import start_web
        from agent.telegram import start_telegram
        token = args[1] if len(args) > 1 else TELEGRAM_TOKEN
        if token:
            start_telegram(token)
        _maybe_start_widget(args)
        start_web()

    else:
        _maybe_start_widget(args)
        from agent.cli import start_cli
        start_cli()


if __name__ == "__main__":
    main()
