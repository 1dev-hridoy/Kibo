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


def main():
    args = sys.argv[1:]
    mode = args[0].lower() if args else "cli"

    if mode == "web":
        from agent.web import start_web
        port = int(args[1]) if len(args) > 1 and args[1].isdigit() else WEB_PORT
        if "--telegram" in args:
            tidx = args.index("--telegram") + 1
            token = args[tidx] if tidx < len(args) else TELEGRAM_TOKEN
            if token:
                from agent.telegram import start_telegram
                start_telegram(token)
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
