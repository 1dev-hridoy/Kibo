<p align="center">
  <img src="assets/kibo.jpg" alt="Kibo" width="600">
</p>

<h1 align="center">
  <img src="assets/kibo-b-app-tile.svg" alt="Kibo logo" width="48"><br>
  Kibo
</h1>

<p align="center">
  <b>Your PC, controlled by chat.</b><br>
  130 tools • Local AI • No cloud
</p>

<p align="center">
  <img src="https://img.shields.io/badge/version-2.0.0-blue" alt="Version">
  <img src="https://img.shields.io/badge/python-3.10+-green" alt="Python">
  <img src="https://img.shields.io/badge/license-MIT-green" alt="License">
  <img src="https://img.shields.io/badge/tools-130-purple" alt="Tools">
  <a href="https://kibo.0git.site/">Website</a> •
  <a href="https://github.com/1dev-hridoy/Kibo">GitHub</a>
</p>

---

Kibo is a local-first AI agent that automates your workflow through
natural language. **No cloud. No API keys. Your data stays private.**

```
Loading Needle 2 (14MB)...
Agent ready — 130 tools registered.
You: set volume to 80
Kibo: Volume set to 80. ✓
```

---

## See it in action

**Desktop pet widget** — a space companion at the top of your screen.
Idle shows clock + system info, work shows live status, done plays
confetti. Click to poke it, triple-click for dizzy.

**Web UI** — chat at `/`, searchable tool list at `/tools`,
live screen, terminal, macros, model switching.

**Telegram** — control your PC from your phone, with buttons,
voice, screenshots and live tool updates.

---

## Install

```bash
curl -sL https://raw.githubusercontent.com/1dev-hridoy/Kibo/main/install.sh | bash
```

Windows (PowerShell): `powershell -ExecutionPolicy Bypass -File install.ps1`

## Setup

- **Autostart (optional):** first run asks if Kibo starts with your PC.
- **Telegram (optional):** `./run.sh telegram` asks for bot token,
  group chat id and user id. More chats: `/allow <chat_id>`.

## Use

```bash
cd ~/kibo
./run.sh              # terminal chat
./run.sh web          # browser UI + widget
./run.sh telegram     # telegram bot + widget
./run.sh all          # web + telegram
```

---

## All tools (130) with examples

### 🖥️ System

| Say | Tool |
|-----|------|
| `show a notification saying done` | `show_notification` |
| `check battery` | `get_battery_status` |
| `set brightness to 80` | `set_screen_brightness` |
| `volume 80` / `mute` | `set_volume` |
| `lock the screen` | `lock_the_screen` |
| `cpu and ram usage` | `get_system_stats` |
| `device info` | `get_device_info` |
| `take a screenshot` | `take_screenshot_now` |
| `shutdown the pc` | `power_control` |
| `check system health` | `check_system_health` |
| `show disk usage` | `get_disk_usage` |
| `show temperature` | `get_temperature` |
| `view system logs` | `view_system_logs` |
| `toast hello` | `show_toast` |

### 📁 Files & apps

| Say | Tool |
|-----|------|
| `list files in downloads` | `list_files` |
| `list installed apps` | `list_installed_apps` |
| `open firefox` / `open youtube` | `open_app` |
| `create file notes.txt with hi` | `create_file` |
| `read file /etc/hostname` | `read_file` |
| `show running processes` | `get_running_processes` |
| `install package htop` | `install_package` |
| `run ls -la` | `remote_terminal` |
| `launch firefox smartly` | `launch_app_smart` |
| `copy hello to clipboard` | `set_clipboard` / `copy_text_to_clipboard` |

### 🌐 Network & security

| Say | Tool |
|-----|------|
| `wifi info` / `scan wifi` | `get_wifi_info` / `scan_wifi_networks` |
| `scan my network` | `local_network_scan` |
| `scan ports on 192.168.0.1` | `local_port_scan` |
| `check for arp spoofing` | `detect_arp_spoofing` |
| `audit my vpn` | `audit_vpn_connection` |
| `audit website security example.com` | `audit_website_security` |
| `dns lookup example.com` | `dns_lookup` |
| `whois example.com` | `whois_lookup` |
| `where is 8.8.8.8` | `ip_geolocation_lookup` |
| `hash this file` / `decode this jwt` | `generate_file_checksum` / `decode_jwt_token` |

### 🎙️ Media & voice

| Say | Tool |
|-----|------|
| `play some music` | `play_media` |
| `take a photo` | `take_camera_photo` |
| `say hello out loud` | `text_to_speech` |
| `start listening for hey kibo` | `voice_start_listener` |
| `listen now` | `voice_listen_now` |

### 🐾 Widget, pet & reminders

| Say | Tool |
|-----|------|
| `show hi on the widget` | `widget_set_message` |
| `clear widget` | `widget_clear` |
| `pet show good morning` | `pet_show` / `pet_send` / `pet_love` |
| `dance with kibo` | `pet_animate` |
| `showcase` | all 15 animations, one by one |
| `animations` | animation preview list |
| `drink water` | `remind_water` (+ sound) |
| `touch grass` | `remind_grass` (+ sound) |
| `stretch` / `rest my eyes` / `sit straight` | `remind_stretch` / `remind_eyes` / `remind_posture` |
| `reminders off` | `reminders_on` / `reminders_off` / `reminders_status` |

### ☀️ Briefing & automation

| Say | Tool |
|-----|------|
| `brief` / `brief the day` | `brief_today` (weather, battery, agenda) |
| `briefing off` | `briefing_on` / `briefing_off` |
| `record a macro` / `replay backup` | `start_macro_recording` / `replay_macro` |
| `schedule ...` | `schedule_agent_task` / `schedule_shell_task` |
| `switch gemma` / `models` | model switching |
| `start kibo on boot` | `autostart_enable` / `autostart_disable` |

Plus: window control (`focus_app`, `minimize_app`…), clipboard sync,
alerts, multi-PC (`list_remote_pcs`, `execute_on_remote_pc`), TTS/STT
variants — 130 total, see `/tools` in the web UI.

---

## How it works

1. **Install** — one command, local virtualenv, pick a model.
2. **Start** — `./run.sh web` (or cli / telegram).
3. **Use** — type naturally; deterministic fast-paths handle common
   commands instantly, the local model handles the rest. Nothing leaves
   your machine.

---

## Docs

- [Creating tools](docs/TOOLS.md) — add your own capabilities
- [Animations, widget & sounds](docs/ANIMATIONS.md) — pet fx, expand/collapse, sound rules

## License

MIT — built by [1dev-hridoy](https://github.com/1dev-hridoy)
