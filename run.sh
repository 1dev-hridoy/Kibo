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




echo "⚠ No venv found — creating one now..."
if ! command -v python3 >/dev/null 2>&1; then
    echo "✖ python3 is required. Install it first."
    exit 1
fi
python3 -m venv "$DIR/.venv" || { echo "✖ Could not create venv (try: sudo apt install python3-venv)"; exit 1; }
"$DIR/.venv/bin/pip" install --quiet --upgrade pip >/dev/null 2>&1 || true
"$DIR/.venv/bin/pip" install -e "$DIR" || { echo "✖ pip install failed"; exit 1; }
echo "✔ venv ready at $DIR/.venv"
exec "$DIR/.venv/bin/python" -m agent "$@"
