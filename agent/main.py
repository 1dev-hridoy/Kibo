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
        if not token:
            print("Error: Provide Telegram bot token.")
            print("Usage: python -m agent telegram YOUR_BOT_TOKEN")
            print("Or set AGENT_TELEGRAM_TOKEN env var.")
            sys.exit(1)
        from agent.telegram import start_telegram
        start_telegram(token)
        import time
        while True:
            time.sleep(60)

    elif mode == "all":
        from agent.web import start_web
        from agent.telegram import start_telegram
        token = args[1] if len(args) > 1 else TELEGRAM_TOKEN
        if token:
            start_telegram(token)
        start_web()

    else:
        from agent.cli import start_cli
        start_cli()


if __name__ == "__main__":
    main()
