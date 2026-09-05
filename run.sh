#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────
#  KIBO · quick launcher (Linux/macOS)
#
#  Usage:
#    ./run.sh                 # Interactive CLI
#    ./run.sh web [PORT]      # Web UI  (default http://127.0.0.1:5000)
#    ./run.sh telegram TOKEN  # Telegram bot
#    ./run.sh all [TOKEN]     # Web + Telegram
#
#  Auto-detects the venv created by install.sh; falls back to the
#  system interpreter (may hit PEP 668 restrictions — prefer a venv).
# ─────────────────────────────────────────────────────────────
set -e
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

for V in "$DIR/venv" "$DIR/.venv" "$DIR/../venv" "$DIR/../.venv"; do
    if [ -x "$V/bin/python" ]; then
        exec "$V/bin/python" -m agent "$@"
    fi
done

echo "⚠ No venv found — run ./install.sh first (recommended)."
exec python3 -m agent "$@"
