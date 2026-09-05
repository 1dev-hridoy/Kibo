#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════════════
#  Kibo — Updater
#  Usage: ./update.sh
# ═══════════════════════════════════════════════════════════════════════
set -e

BOLD='\033[1m'; DIM='\033[2m'; GREEN='\033[32m'; YELLOW='\033[33m'
RED='\033[31m'; CYAN='\033[36m'; WHITE='\033[37m'; NC='\033[0m'

ok()    { printf "  ${GREEN}✔${NC} %s\n" "$1"; }
warn()  { printf "  ${YELLOW}⚠${NC} %s\n" "$1"; }
fail()  { printf "  ${RED}✖${NC} %s\n" "$1"; exit 1; }
info()  { printf "  ${CYAN}●${NC} %s\n" "$1"; }
step()  { printf "\n${BOLD}${CYAN}[%s]${NC} ${BOLD}%s${NC}\n" "$1" "$2"; }
line()  { printf "  ${DIM}────────────────────────────────────────${NC}\n"; }

printf "\n  ${BOLD}${CYAN}KIBO — Updater${NC}\n"
printf "  ─────────────────\n\n"

# ── [1] Find install ────────────────────────────────────────────────
step "1/4" "Checking installation"
line

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR" || fail "Could not enter $DIR"

# Find venv
VENV=""
for v in venv .venv; do
    if [ -x "$DIR/$v/bin/python" ]; then
        VENV="$DIR/$v"
        break
    fi
done
[ -z "$VENV" ] && fail "No venv found. Run install.sh first."
ok "Found venv: $VENV"

# ── [2] Check current vs remote ─────────────────────────────────────
step "2/4" "Checking for updates"
line

CURRENT=$("$VENV/bin/python" -c "import agent; print(agent.__version__)" 2>/dev/null || echo "0.0.0")
ok "Current version: $CURRENT"

info "Fetching latest from GitHub..."
git fetch --quiet origin main 2>/dev/null || fail "Could not reach GitHub. Check your internet."

REMOTE=$(git log origin/main -1 --format="%H" 2>/dev/null)
LOCAL=$(git rev-parse HEAD 2>/dev/null)

if [ "$REMOTE" = "$LOCAL" ]; then
    ok "Already up to date (v$CURRENT)"
    printf "\n  ${GREEN}No updates available.${NC}\n\n"
    exit 0
fi

# Get remote version
REMOTE_VERSION=$("$VENV/bin/python" -c "
import subprocess, re
out = subprocess.check_output(['git', 'show', 'origin/main:agent/__init__.py'], text=True)
m = re.search(r'__version__\s*=\s*\"(.+?)\"', out)
print(m.group(1) if m else 'unknown')
" 2>/dev/null || echo "unknown")

printf "\n"
printf "  ${BOLD}┌─────────────────────────────────────────┐${NC}\n"
printf "  ${BOLD}│${NC}  ${WHITE}Update available!${NC}                       ${BOLD}│${NC}\n"
printf "  ${BOLD}├─────────────────────────────────────────┤${NC}\n"
printf "  ${BOLD}│${NC}                                         ${BOLD}│${NC}\n"
printf "  ${BOLD}│${NC}  ${DIM}Current:${NC}  ${YELLOW}v%-28s${NC} ${BOLD}│${NC}\n" "$CURRENT"
printf "  ${BOLD}│${NC}  ${DIM}Latest:${NC}   ${GREEN}v%-28s${NC} ${BOLD}│${NC}\n" "$REMOTE_VERSION"
printf "  ${BOLD}│${NC}                                         ${BOLD}│${NC}\n"
printf "  ${BOLD}└─────────────────────────────────────────┘${NC}\n"
printf "\n"

# ── [3] Confirm update ──────────────────────────────────────────────
step "3/4" "Applying update"
line

printf "  ${BOLD}Update now? [${GREEN}Y${NC}${BOLD}/n]: ${NC}"
if [ -t 0 ]; then
    read -r CONFIRM
else
    CONFIRM="y"
    printf "y (auto)\n"
fi

if [[ "${CONFIRM,,}" == "n" || "${CONFIRM,,}" == "no" ]]; then
    printf "\n  ${YELLOW}Update cancelled.${NC}\n\n"
    exit 0
fi

info "Pulling latest changes..."
git pull --quiet origin main || fail "Git pull failed"
ok "Code updated"

info "Installing dependencies..."
"$VENV/bin/pip" install --quiet -e . 2>/dev/null || warn "pip install had issues"
ok "Dependencies updated"

# ── [4] Verify ──────────────────────────────────────────────────────
step "4/4" "Verification"
line

NEW_VERSION=$("$VENV/bin/python" -c "import agent; print(agent.__version__)" 2>/dev/null || echo "unknown")
TOOL_COUNT=$("$VENV/bin/python" -c "from agent.tools import ALL_TOOLS; print(len(ALL_TOOLS))" 2>/dev/null || echo "?")

ok "Version: $NEW_VERSION"
ok "Tools: $TOOL_COUNT"

printf "\n  ${GREEN}Update complete!${NC}\n\n"
printf "  ${BOLD}Restart Kibo:${NC}\n\n"
printf "    ${CYAN}./run.sh${NC}              ${DIM}# terminal chat${NC}\n"
printf "    ${CYAN}./run.sh web${NC}          ${DIM}# browser UI${NC}\n"
printf "    ${CYAN}./run.sh telegram${NC}     ${DIM}# telegram bot${NC}\n\n"
