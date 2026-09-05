"""
App URL maps and native desktop launcher maps.
Separated from config.py for clarity and maintainability.
"""

# ── Web app URLs (opened with the default browser) ────────────────────
APP_URLS = {
    "youtube": "https://www.youtube.com",
    "yt": "https://www.youtube.com",
    "whatsapp": "https://web.whatsapp.com",
    "wa": "https://web.whatsapp.com",
    "chrome": "https://google.com",
    "google": "https://google.com",
    "browser": "https://google.com",
    "instagram": "https://instagram.com",
    "insta": "https://instagram.com",
    "spotify": "https://open.spotify.com",
    "telegram": "https://t.me",
    "facebook": "https://facebook.com",
    "fb": "https://facebook.com",
    "twitter": "https://twitter.com",
    "x": "https://x.com",
    "gmail": "https://mail.google.com",
    "maps": "https://maps.google.com",
    "google maps": "https://maps.google.com",
}

# ── Native desktop app launchers ──────────────────────────────────────
# Linux: command lists executed directly
LINUX_APPS = {
    "calculator": ["gnome-calculator"],
    "settings": ["gnome-control-center"],
    "files": ["nautilus"],
    "file manager": ["nautilus"],
    "text editor": ["gedit"],
    "editor": ["gedit"],
    "terminal": ["xterm"],
    "kitty": ["kitty"],
    "alacritty": ["alacritty"],
    "wezterm": ["wezterm"],
    "tilix": ["tilix"],
    "konsole": ["konsole"],
    "gnome terminal": ["gnome-terminal"],
    "xfce4 terminal": ["xfce4-terminal"],
    "lxterminal": ["lxterminal"],
    "mate terminal": ["mate-terminal"],
    "terminology": ["terminology"],
    "yakuake": ["yakuake"],
    "dropdown terminal": ["yakuake"],
    "camera": ["snapshot"],
    "music": ["rhythmbox"],
    "code": ["code"],
    "vscode": ["code"],
    "firefox": ["firefox"],
    "chrome": ["google-chrome"],
    "browser": ["firefox"],
}

# Windows: executable names / URI schemes (opened via ShellExecute)
WINDOWS_APPS = {
    "calculator": ["calc.exe"],
    "calc": ["calc.exe"],
    "notepad": ["notepad.exe"],
    "text editor": ["notepad.exe"],
    "editor": ["notepad.exe"],
    "files": ["explorer.exe"],
    "file manager": ["explorer.exe"],
    "file explorer": ["explorer.exe"],
    "settings": ["ms-settings:"],
    "terminal": ["cmd.exe"],
    "cmd": ["cmd.exe"],
    "paint": ["mspaint.exe"],
    "camera": ["microsoft.windows.camera:"],
    "code": ["code"],
    "vscode": ["code"],
    "chrome": ["chrome"],
    "edge": ["msedge"],
    "spotify": ["spotify"],
    "firefox": ["firefox"],
}

# macOS: app names passed to `open -a`
MACOS_APPS = {
    "calculator": ["Calculator"],
    "settings": ["System Settings"],
    "files": ["Finder"],
    "file manager": ["Finder"],
    "text editor": ["TextEdit"],
    "editor": ["TextEdit"],
    "terminal": ["Terminal"],
    "camera": ["Photo Booth"],
    "music": ["Music"],
    "code": ["Visual Studio Code"],
    "vscode": ["Visual Studio Code"],
    "safari": ["Safari"],
}
