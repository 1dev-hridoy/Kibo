# Kibo

Your PC, controlled by chat.

Kibo is a local AI agent that runs on your computer. Talk to it in
terminal, browser, or Telegram — it handles the rest.

Set volume, take screenshots, open apps, check battery, run commands,
manage files, stream music, record voice. 57 tools, all local.

**No cloud. No API keys. Your data stays on your machine.**

---

## Install

```bash
curl -sL https://raw.githubusercontent.com/1dev-hridoy/Kibo/main/install.sh | bash
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

## What can it do

**System** — volume, brightness, battery, screenshots, lock screen, shutdown

**Files** — list, create, delete, move, read files & folders

**Apps** — open any app, browser, website

**Terminal** — run any shell command (`ls`, `git status`, `python --version`)

**Network** — wifi info, scan networks, check internet

**Media** — play music/videos from URLs, record voice, text-to-speech

**Clipboard** — copy, paste, sync across devices

**Processes** — list running apps, kill processes

**Packages** — install/uninstall software

**And more** — 57 tools total, just ask naturally

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

| Model | Size | Speed | Best for |
|-------|------|-------|----------|
| Needle 2 | 14 MB | Fast | Quick commands, low RAM |
| FunctionGemma | 253 MB | Smarter | Better reasoning |

Switch anytime: type `needle` or `gemma`

---

## Requirements

- Python 3.9+
- Linux, Windows, or macOS

---

## License

MIT

---

Built by [1dev-hridoy](https://github.com/1dev-hridoy)
