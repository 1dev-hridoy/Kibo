<p align="center">
  <img src="https://raw.githubusercontent.com/1dev-hridoy/1dev-hridoy/refs/heads/main/kibo_banner.png" alt="Kibo" width="600">
</p>

<h1 align="center">Kibo</h1>

<p align="center">
  <b>Your PC, controlled by chat.</b><br>
  57 tools • Local AI • No cloud
</p>

<p align="center">
  <img src="https://img.shields.io/badge/version-1.0.0-blue" alt="Version">
  <img src="https://img.shields.io/badge/python-3.10+-green" alt="Python">
  <img src="https://img.shields.io/badge/license-MIT-green" alt="License">
  <img src="https://img.shields.io/badge/tools-57-purple" alt="Tools">
</p>

---

Kibo is a local AI agent that runs on your computer. Talk to it in
terminal, browser, or Telegram — it handles the rest.

Set volume, take screenshots, open apps, check battery, run commands,
manage files, stream music, record voice. **57 tools**, all local.

**No cloud. No API keys. Your data stays on your machine.**

---

## Install

**Quick (one command):**
```bash
curl -sL https://raw.githubusercontent.com/1dev-hridoy/Kibo/main/install.sh | bash
```

**With model selection:**
```bash
curl -sLO https://raw.githubusercontent.com/1dev-hridoy/Kibo/main/install.sh
chmod +x install.sh
./install.sh
```

---

## Run

```bash
cd ~/kibo
./run.sh              # terminal chat
./run.sh web          # browser (localhost:5000)
./run.sh telegram     # telegram bot
```

---

## Update

```bash
cd ~/kibo
./update.sh
```

---

## Uninstall

```bash
cd ~/kibo
./uninstall.sh
```

---

## What can it do

| Category | Tools |
|----------|-------|
| **System** | Volume, brightness, battery, screenshots, lock screen, shutdown |
| **Files** | List, create, delete, move, read files & folders |
| **Apps** | Open any app, browser, website |
| **Terminal** | Run any shell command (`ls`, `git status`, `python --version`) |
| **Network** | WiFi info, scan networks, check internet |
| **Media** | Play music/videos from URLs, record voice, text-to-speech |
| **Clipboard** | Copy, paste, sync across devices |
| **Processes** | List running apps, kill processes |
| **Packages** | Install/uninstall software |
| **Advanced** | Remote terminal, app launcher, clipboard sync, media streamer, voice gateway |

---

## Quick commands

```
ls                          # list files
view downloads              # open Downloads folder
battery                     # check battery
volume 80                   # set volume
screenshot                  # take screenshot
open firefox                # launch app
run echo hello              # run command
processes                   # show running apps
models                      # switch AI models
```

---

## Models

Kibo supports two local AI models:

| Model | Size | Speed | Best for |
|-------|------|-------|----------|
| Needle 2 | 14 MB | Fast | Quick commands, low RAM |
| FunctionGemma | 253 MB | Smarter | Better reasoning |

Switch anytime: type `needle` or `gemma`

---

## Requirements

- Python 3.10+
- Linux, Windows, or macOS

---

## Project Structure

```
kibo/
├── agent/
│   ├── __init__.py         # Version
│   ├── main.py             # Entry point
│   ├── cli.py              # Interactive CLI
│   ├── config.py           # Platform config
│   ├── logs.py             # Logging
│   ├── model_manager.py    # AI model switching
│   ├── core/               # AI engine, fast-path, prompt
│   ├── runner/             # Tool runners (18 modules)
│   ├── tools/              # Tool registry (57 tools)
│   ├── web/                # Flask web UI
│   └── telegram/           # Telegram bot
├── install.sh              # Linux/macOS installer
├── install.ps1             # Windows installer
├── run.sh                  # Quick launcher
├── update.sh               # Updater
├── uninstall.sh            # Uninstaller
└── pyproject.toml          # Package config
```

---

## License

MIT

---

<p align="center">
  Built by <a href="https://github.com/1dev-hridoy">1dev-hridoy</a>
</p>
