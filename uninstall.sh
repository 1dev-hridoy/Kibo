#!/usr/bin/env bash
# KIBO · uninstaller (Linux/macOS)
# Removes the venv, the desktop entry and (with --purge) helper packages.
set -e
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Uninstalling Kibo..."

for v in venv .venv; do
    if [ -d "$DIR/$v" ]; then
        rm -rf "$DIR/$v" && echo "✔ $v removed"
    fi
done
rm -f "$HOME/.local/share/applications/kibo.desktop" \
      "$HOME/.local/share/applications/agent.desktop" \
      "$HOME/.local/share/applications/harness.desktop" \
      "$HOME/.local/share/applications/harness-arch.desktop" \
      && echo "✔ desktop entry removed" 2>/dev/null || true

if [ "${1:-}" = "--purge" ]; then
    echo "→ Purging native helper packages (best-effort per distro)…"
    if command -v pacman >/dev/null 2>&1; then
        for p in espeak-ng brightnessctl wl-clipboard xclip scrot; do
            pacman -Q "$p" >/dev/null 2>&1 && sudo pacman -Rns --noconfirm "$p" \
                && echo "✔ $p removed" || echo "✖ $p kept"
        done
    elif command -v apt >/dev/null 2>&1; then
        sudo apt remove -y espeak-ng brightnessctl wl-clipboard xclip scrot 2>/dev/null || true
    elif command -v dnf >/dev/null 2>&1; then
        sudo dnf remove -y espeak-ng brightnessctl wl-clipboard xclip scrot 2>/dev/null || true
    fi
fi

echo "Done. Source files remain in $DIR (remove manually if unwanted)."
