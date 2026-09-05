"""
Telegram bot — remote PC control via text messages.
Sends screenshots and webcam photos as images, not text.
Includes PID lock to prevent multiple instances.
"""

import sys
import os
import signal
import threading

from agent.core import ask
from agent.logs import user_input, ai_response, error, startup, info

PID_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".telegram_bot.pid")


def _acquire_lock():
    """Kill any existing bot instance and claim the PID file."""
    if os.path.exists(PID_FILE):
        try:
            with open(PID_FILE) as f:
                old_pid = int(f.read().strip())
            try:
                os.kill(old_pid, 0)
                info(f"[Telegram] Killing old bot instance (PID {old_pid})...")
                os.kill(old_pid, signal.SIGKILL)
            except (ProcessLookupError, PermissionError):
                pass
        except (ValueError, OSError):
            pass
        os.remove(PID_FILE)
    with open(PID_FILE, "w") as f:
        f.write(str(os.getpid()))


def _release_lock():
    """Remove PID file on exit."""
    try:
        if os.path.exists(PID_FILE):
            with open(PID_FILE) as f:
                if int(f.read().strip()) == os.getpid():
                    os.remove(PID_FILE)
    except (ValueError, OSError):
        pass


def start_telegram(token: str):
    """Start a Telegram bot listener in a background thread."""
    _acquire_lock()

    try:
        import telebot
    except ImportError:
        print("Error: pyTelegramBotAPI not installed. Run: pip install pyTelegramBotAPI")
        _release_lock()
        return

    bot = telebot.TeleBot(token, parse_mode="HTML")
    startup("Telegram", "Bot active — listening for messages")

    @bot.message_handler(func=lambda m: True)
    def handle(message):
        user_text = message.text.strip()
        if not user_text:
            return

        user_input("telegram", user_text)

        try:
            result = ask(user_text)
            text = result.get("text", "")
            media = result.get("media")

            ai_response("telegram", text, result.get("tool_calls"), result.get("results"))

            if media and media.get("path") and os.path.exists(media["path"]):
                caption = text if text else ("Screenshot" if media["type"] == "screenshot" else "Photo")
                if len(caption) > 1000:
                    caption = caption[:1000] + "..."
                try:
                    with open(media["path"], "rb") as photo:
                        bot.send_photo(message.chat.id, photo, caption=caption)
                    return
                except Exception as e:
                    error("telegram", f"Failed to send photo: {e}")

            if text:
                if len(text) > 4000:
                    for i in range(0, len(text), 4000):
                        bot.reply_to(message, text[i:i+4000])
                else:
                    bot.reply_to(message, text)
            else:
                bot.reply_to(message, "Done.")

        except Exception as e:
            error("telegram", str(e))
            bot.reply_to(message, f"Error: {e}")

    @bot.message_handler(commands=["start", "help"])
    def send_welcome(message):
        user_input("telegram", "/start")
        bot.reply_to(message,
            "I'm Kibo — your local PC agent. Send me any command:\n\n"
            "Examples:\n"
            "- set volume to 80\n"
            "- take a screenshot\n"
            "- battery status\n"
            "- wifi info\n"
            "- list running processes\n"
            "- disk usage\n"
            "- view system logs\n\n"
            "Type 'tools' to see all 57 available tools.")

    import atexit
    atexit.register(_release_lock)

    def signal_handler(sig, frame):
        _release_lock()
        sys.exit(0)
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    thread = threading.Thread(target=bot.infinity_polling, daemon=True)
    thread.start()
    info("[Telegram] Listener running in background.")
