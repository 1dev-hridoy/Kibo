"""
Telegram bot — remote PC control via text messages.
Supports inline keyboards, bot commands, and media sending.
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


def _build_main_keyboard():
    """Build the main quick-action inline keyboard."""
    from telebot import types
    keyboard = types.InlineKeyboardMarkup(row_width=2)

    # Row 1: System
    keyboard.row(
        types.InlineKeyboardButton("🔋 Battery", callback_data="cmd_battery"),
        types.InlineKeyboardButton("📶 WiFi", callback_data="cmd_wifi"),
    )
    # Row 2: Volume & Brightness
    keyboard.row(
        types.InlineKeyboardButton("🔊 Volume Up", callback_data="cmd_vol_up"),
        types.InlineKeyboardButton("🔉 Volume Down", callback_data="cmd_vol_down"),
    )
    keyboard.row(
        types.InlineKeyboardButton("🔆 Bright+", callback_data="cmd_bright_up"),
        types.InlineKeyboardButton("🔅 Bright-", callback_data="cmd_bright_down"),
    )
    # Row 3: Screenshots & Media
    keyboard.row(
        types.InlineKeyboardButton("📸 Screenshot", callback_data="cmd_screenshot"),
        types.InlineKeyboardButton("📷 Webcam", callback_data="cmd_webcam"),
    )
    # Row 4: System Info
    keyboard.row(
        types.InlineKeyboardButton("💻 PC Info", callback_data="cmd_pc_info"),
        types.InlineKeyboardButton("📊 CPU/RAM", callback_data="cmd_stats"),
    )
    # Row 5: Processes
    keyboard.row(
        types.InlineKeyboardButton("⚙️ Processes", callback_data="cmd_processes"),
        types.InlineKeyboardButton("🌡️ Temperature", callback_data="cmd_temp"),
    )
    # Row 6: Files & Apps
    keyboard.row(
        types.InlineKeyboardButton("📁 Files", callback_data="cmd_files"),
        types.InlineKeyboardButton("📱 Apps", callback_data="cmd_apps"),
    )
    # Row 7: Actions
    keyboard.row(
        types.InlineKeyboardButton("🔒 Lock", callback_data="cmd_lock"),
        types.InlineKeyboardButton("🔊 Mute", callback_data="cmd_mute"),
    )
    # Row 8: Model & Help
    keyboard.row(
        types.InlineKeyboardButton("🤖 Model", callback_data="cmd_model"),
        types.InlineKeyboardButton("❓ Help", callback_data="cmd_help"),
    )

    return keyboard


def _build_model_keyboard():
    """Build model selection keyboard."""
    from telebot import types
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.row(
        types.InlineKeyboardButton("⚡ Needle (14MB)", callback_data="switch_needle"),
        types.InlineKeyboardButton("🧠 FunctionGemma (253MB)", callback_data="switch_functiongemma"),
    )
    keyboard.row(
        types.InlineKeyboardButton("🔙 Back", callback_data="cmd_help"),
    )
    return keyboard


def _handle_callback(bot, call):
    """Handle inline keyboard callback queries."""
    data = call.data
    chat_id = call.message.chat.id

    # Show typing indicator
    bot.send_chat_action(chat_id, "typing")

    # Route callback to command
    command_map = {
        "cmd_battery": "battery status",
        "cmd_wifi": "wifi info",
        "cmd_vol_up": "volume up",
        "cmd_vol_down": "volume down",
        "cmd_bright_up": "brightness up",
        "cmd_bright_down": "brightness down",
        "cmd_screenshot": "take a screenshot",
        "cmd_webcam": "take a photo",
        "cmd_pc_info": "device info",
        "cmd_stats": "cpu and ram usage",
        "cmd_processes": "show running processes",
        "cmd_temp": "show temperature",
        "cmd_files": "list files in home",
        "cmd_apps": "list installed apps",
        "cmd_lock": "lock the screen",
        "cmd_mute": "mute volume",
        "cmd_help": "__show_help__",
        "cmd_model": "__show_model__",
    }

    if data == "switch_needle":
        from agent.model_manager import switch_model
        from agent.core.engine import reload_backend
        success, msg = switch_model("needle")
        if success:
            reload_backend()
        bot.answer_callback_query(call.id, "Switched to Needle")
        bot.edit_message_text(msg, chat_id, call.message.message_id)
        return

    if data == "switch_functiongemma":
        from agent.model_manager import switch_model
        from agent.core.engine import reload_backend
        success, msg = switch_model("functiongemma")
        if success:
            reload_backend()
        bot.answer_callback_query(call.id, "Switched to FunctionGemma")
        bot.edit_message_text(msg, chat_id, call.message.message_id)
        return

    if data == "__show_help__":
        bot.answer_callback_query(call.id)
        bot.edit_message_text(
            _get_help_text(),
            chat_id, call.message.message_id,
            parse_mode="HTML",
            reply_markup=_build_main_keyboard()
        )
        return

    if data == "__show_model__":
        from agent.model_manager import get_active_model, MODELS
        current = get_active_model()
        info = MODELS.get(current, {})
        bot.answer_callback_query(call.id)
        bot.edit_message_text(
            f"Current model: <b>{info.get('name', current)}</b>\n"
            f"Size: {info.get('size', 'Unknown')}\n\n"
            f"Select a model:",
            chat_id, call.message.message_id,
            parse_mode="HTML",
            reply_markup=_build_model_keyboard()
        )
        return

    if data in command_map:
        bot.answer_callback_query(call.id)
        user_text = command_map[data]
        user_input("telegram", user_text)

        try:
            result = ask(user_text)
            text = result.get("text", "")
            media = result.get("media")
            tool_calls = result.get("tool_calls", [])

            # Format tool calls
            tools_text = ""
            if tool_calls:
                tools_text = "\n\n<i>Tools: " + ", ".join(
                    tc.get("name", "") for tc in tool_calls
                ) + "</i>"

            ai_response("telegram", text, tool_calls, result.get("results"))

            if media and media.get("path") and os.path.exists(media["path"]):
                caption = (text or "Result") + tools_text
                if len(caption) > 1000:
                    caption = caption[:1000] + "..."
                try:
                    with open(media["path"], "rb") as photo:
                        bot.send_photo(chat_id, photo, caption=caption, parse_mode="HTML")
                    return
                except Exception as e:
                    error("telegram", f"Failed to send photo: {e}")

            if text:
                full_text = text + tools_text
                if len(full_text) > 4000:
                    for i in range(0, len(full_text), 4000):
                        bot.reply_to(call.message, full_text[i:i+4000], parse_mode="HTML")
                else:
                    bot.reply_to(call.message, full_text, parse_mode="HTML")
            else:
                bot.reply_to(call.message, "Done.")

        except Exception as e:
            error("telegram", str(e))
            bot.reply_to(call.message, f"Error: {e}")


def _get_help_text():
    """Get formatted help text."""
    return (
        "🤖 <b>Kibo — Your PC Agent</b>\n\n"
        "Send any command naturally, or use these shortcuts:\n\n"
        "📱 <b>Quick Commands:</b>\n"
        "• <code>/screenshot</code> — Take screenshot\n"
        "• <code>/battery</code> — Check battery\n"
        "• <code>/volume 80</code> — Set volume\n"
        "• <code>/wifi</code> — WiFi info\n"
        "• <code>/lock</code> — Lock screen\n"
        "• <code>/processes</code> — Running apps\n"
        "• <code>/stats</code> — CPU/RAM usage\n"
        "• <code>/temp</code> — Temperature\n"
        "• <code>/model</code> — Switch AI model\n\n"
        "💡 <b>Natural Language:</b>\n"
        "Just type what you want:\n"
        "• \"open firefox\"\n"
        "• \"set brightness to 50\"\n"
        "• \"show disk usage\"\n"
        "• \"run ls -la\"\n\n"
        "Use the buttons below for quick actions! 👇"
    )


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

    # ── Command handlers ─────────────────────────────────────────────
    @bot.message_handler(commands=["start", "help"])
    def send_welcome(message):
        user_input("telegram", "/start")
        bot.reply_to(message, _get_help_text(), reply_markup=_build_main_keyboard())

    @bot.message_handler(commands=["screenshot", "ss"])
    def cmd_screenshot(message):
        user_input("telegram", "/screenshot")
        bot.send_chat_action(message.chat.id, "upload_photo")
        try:
            result = ask("take a screenshot")
            text = result.get("text", "")
            media = result.get("media")
            if media and media.get("path") and os.path.exists(media["path"]):
                with open(media["path"], "rb") as photo:
                    bot.send_photo(message.chat.id, photo, caption=text or "Screenshot")
            else:
                bot.reply_to(message, text or "Screenshot taken")
        except Exception as e:
            bot.reply_to(message, f"Error: {e}")

    @bot.message_handler(commands=["battery", "bat"])
    def cmd_battery(message):
        _run_command(bot, message, "battery status")

    @bot.message_handler(commands=["wifi", "network"])
    def cmd_wifi(message):
        _run_command(bot, message, "wifi info")

    @bot.message_handler(commands=["volume", "vol"])
    def cmd_volume(message):
        args = message.text.split(maxsplit=1)
        if len(args) > 1:
            _run_command(bot, message, f"volume {args[1]}")
        else:
            _run_command(bot, message, "what is the current volume")

    @bot.message_handler(commands=["brightness", "bright"])
    def cmd_brightness(message):
        args = message.text.split(maxsplit=1)
        if len(args) > 1:
            _run_command(bot, message, f"brightness {args[1]}")
        else:
            _run_command(bot, message, "what is the brightness")

    @bot.message_handler(commands=["lock"])
    def cmd_lock(message):
        _run_command(bot, message, "lock the screen")

    @bot.message_handler(commands=["mute"])
    def cmd_mute(message):
        _run_command(bot, message, "mute volume")

    @bot.message_handler(commands=["processes", "ps"])
    def cmd_processes(message):
        _run_command(bot, message, "show running processes")

    @bot.message_handler(commands=["stats", "cpu", "ram"])
    def cmd_stats(message):
        _run_command(bot, message, "cpu and ram usage")

    @bot.message_handler(commands=["temp", "temperature"])
    def cmd_temp(message):
        _run_command(bot, message, "show temperature")

    @bot.message_handler(commands=["disk", "storage"])
    def cmd_disk(message):
        _run_command(bot, message, "disk usage")

    @bot.message_handler(commands=["apps", "installed"])
    def cmd_apps(message):
        _run_command(bot, message, "list installed apps")

    @bot.message_handler(commands=["files", "ls"])
    def cmd_files(message):
        args = message.text.split(maxsplit=1)
        if len(args) > 1:
            _run_command(bot, message, f"list files in {args[1]}")
        else:
            _run_command(bot, message, "list files in home")

    @bot.message_handler(commands=["logs"])
    def cmd_logs(message):
        _run_command(bot, message, "view system logs")

    @bot.message_handler(commands=["model"])
    def cmd_model(message):
        from agent.model_manager import get_active_model, MODELS
        current = get_active_model()
        info = MODELS.get(current, {})
        bot.reply_to(message,
            f"Current model: <b>{info.get('name', current)}</b>\n"
            f"Size: {info.get('size', 'Unknown')}\n\n"
            f"Select a model:",
            reply_markup=_build_model_keyboard()
        )

    @bot.message_handler(commands=["webcam", "camera"])
    def cmd_webcam(message):
        _run_command(bot, message, "take a photo")

    @bot.message_handler(commands=["notify", "toast"])
    def cmd_notify(message):
        args = message.text.split(maxsplit=1)
        if len(args) > 1:
            _run_command(bot, message, f"show notification saying {args[1]}")
        else:
            bot.reply_to(message, "Usage: /notify <message>")

    @bot.message_handler(commands=["run", "exec"])
    def cmd_run(message):
        args = message.text.split(maxsplit=1)
        if len(args) > 1:
            _run_command(bot, message, f"run {args[1]}")
        else:
            bot.reply_to(message, "Usage: /run <command>")

    @bot.message_handler(commands=["open"])
    def cmd_open(message):
        args = message.text.split(maxsplit=1)
        if len(args) > 1:
            _run_command(bot, message, f"open {args[1]}")
        else:
            bot.reply_to(message, "Usage: /open <app>")

    # ── Callback query handler ───────────────────────────────────────
    @bot.callback_query_handler(func=lambda call: True)
    def handle_callback(call):
        _handle_callback(bot, call)

    # ── Default message handler ──────────────────────────────────────
    @bot.message_handler(func=lambda m: True)
    def handle(message):
        user_text = message.text.strip()
        if not user_text:
            return

        user_input("telegram", user_text)

        # Show typing indicator
        bot.send_chat_action(message.chat.id, "typing")

        try:
            result = ask(user_text)
            text = result.get("text", "")
            media = result.get("media")
            tool_calls = result.get("tool_calls", [])

            # Format tool calls
            tools_text = ""
            if tool_calls:
                tools_text = "\n\n<i>Tools: " + ", ".join(
                    tc.get("name", "") for tc in tool_calls
                ) + "</i>"

            ai_response("telegram", text, tool_calls, result.get("results"))

            if media and media.get("path") and os.path.exists(media["path"]):
                caption = (text or "Result") + tools_text
                if len(caption) > 1000:
                    caption = caption[:1000] + "..."
                try:
                    with open(media["path"], "rb") as photo:
                        bot.send_photo(message.chat.id, photo, caption=caption, parse_mode="HTML")
                    return
                except Exception as e:
                    error("telegram", f"Failed to send photo: {e}")

            if text:
                full_text = text + tools_text
                if len(full_text) > 4000:
                    for i in range(0, len(full_text), 4000):
                        bot.reply_to(message, full_text[i:i+4000], parse_mode="HTML")
                else:
                    bot.reply_to(message, full_text, parse_mode="HTML")
            else:
                bot.reply_to(message, "Done.")

        except Exception as e:
            error("telegram", str(e))
            bot.reply_to(message, f"Error: {e}")

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


def _run_command(bot, message, command):
    """Run a command with typing indicator."""
    bot.send_chat_action(message.chat.id, "typing")
    user_input("telegram", command)
    try:
        result = ask(command)
        text = result.get("text", "")
        media = result.get("media")
        tool_calls = result.get("tool_calls", [])

        # Format tool calls
        tools_text = ""
        if tool_calls:
            tools_text = "\n\n<i>Tools: " + ", ".join(
                tc.get("name", "") for tc in tool_calls
            ) + "</i>"

        ai_response("telegram", text, tool_calls, result.get("results"))

        if media and media.get("path") and os.path.exists(media["path"]):
            caption = (text or "Result") + tools_text
            if len(caption) > 1000:
                caption = caption[:1000] + "..."
            try:
                with open(media["path"], "rb") as photo:
                    bot.send_photo(message.chat.id, photo, caption=caption, parse_mode="HTML")
                return
            except Exception as e:
                error("telegram", f"Failed to send photo: {e}")

        if text:
            full_text = text + tools_text
            if len(full_text) > 4000:
                for i in range(0, len(full_text), 4000):
                    bot.reply_to(message, full_text[i:i+4000], parse_mode="HTML")
            else:
                bot.reply_to(message, full_text, parse_mode="HTML")
        else:
            bot.reply_to(message, "Done.")

    except Exception as e:
        error("telegram", str(e))
        bot.reply_to(message, f"Error: {e}")
