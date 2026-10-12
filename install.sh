#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════════════
#  Kibo — One-line Installer
#  Usage: curl -sL https://raw.githubusercontent.com/1dev-hridoy/Kibo/main/install.sh | bash
# ═══════════════════════════════════════════════════════════════════════
set -e

MODEL_PRESET=""




BOLD='\033[1m'
DIM='\033[2m'
GREEN='\033[32m'
YELLOW='\033[33m'
RED='\033[31m'
CYAN='\033[36m'
BLUE='\033[34m'
MAGENTA='\033[35m'
WHITE='\033[37m'
NC='\033[0m'




CHECK="${GREEN}✔${NC}"
CROSS="${RED}✖${NC}"
WARN="${YELLOW}⚠${NC}"
ARROW="${CYAN}→${NC}"
DOT="${BLUE}●${NC}



"

ok()    { printf "  ${CHECK} %s\n" "$1"; }
warn()  { printf "  ${WARN} %s\n" "$1"; }
fail()  { printf "  ${CROSS} %s\n" "$1"; exit 1; }
info()  { printf "  ${DOT} %s\n" "$1"; }
step()  { printf "\n${BOLD}${CYAN}[%s]${NC} ${BOLD}%s${NC}\n" "$1" "$2"; }
line()  { printf "  ${DIM}────────────────────────────────────────${NC}\n"; }





show_banner() {
    clear
    printf "\n"
    printf "  ${BOLD}${CYAN}╔════════════════════════════════════════════════════╗${NC}\n"
    printf "  ${BOLD}${CYAN}║${NC}                                                    ${BOLD}${CYAN}║${NC}\n"
    printf "  ${BOLD}${CYAN}║${NC}    ${BOLD}${WHITE}██╗  ██╗██╗██████╗  ██████╗${NC}                  ${BOLD}${CYAN}║${NC}\n"
    printf "  ${BOLD}${CYAN}║${NC}    ${BOLD}${WHITE}██║ ██╔╝██║██╔══██╗██╔═══██╗${NC}                 ${BOLD}${CYAN}║${NC}\n"
    printf "  ${BOLD}${CYAN}║${NC}    ${BOLD}${WHITE}█████╔╝ ██║██████╔╝██║   ██║${NC}                 ${BOLD}${CYAN}║${NC}\n"
    printf "  ${BOLD}${CYAN}║${NC}    ${BOLD}${WHITE}██╔═██╗ ██║██╔══██╗██║   ██║${NC}                 ${BOLD}${CYAN}║${NC}\n"
    printf "  ${BOLD}${CYAN}║${NC}    ${BOLD}${WHITE}██║  ██╗██║██████╔╝╚██████╔╝${NC}                 ${BOLD}${CYAN}║${NC}\n"
    printf "  ${BOLD}${CYAN}║${NC}    ${BOLD}${WHITE}╚═╝  ╚═╝╚═╝╚═════╝  ╚═════╝${NC}                  ${BOLD}${CYAN}║${NC}\n"
    printf "  ${BOLD}${CYAN}║${NC}                                                    ${BOLD}${CYAN}║${NC}\n"
    printf "  ${BOLD}${CYAN}║${NC}      ${DIM}Your PC, controlled by chat${NC}                     ${BOLD}${CYAN}║${NC}\n"
    printf "  ${BOLD}${CYAN}║${NC}      ${DIM}57 tools • Local AI • No cloud${NC}                  ${BOLD}${CYAN}║${NC}\n"
    printf "  ${BOLD}${CYAN}║${NC}                                                    ${BOLD}${CYAN}║${NC}\n"
    printf "  ${BOLD}${CYAN}╚════════════════════════════════════════════════════╝${NC}\n"
    printf "\n"
}





check_system() {
    step "1/9" "System Check"
    line

    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        OS="Linux"
        DISTRO=$(cat /etc/os-release 2>/dev/null | grep ^NAME= | cut -d'"' -f2 || echo "Unknown")
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macOS"
        DISTRO="macOS"
    elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
        OS="Windows"
        DISTRO="Windows"
    else
        OS="Unknown"
        DISTRO="Unknown"
    fi
    ok "OS: ${OS} (${DISTRO})"




    if command -v python3 >/dev/null 2>&1; then
        PYTHON_VER=$(python3 --version 2>&1 | awk '{print $2}')
        ok "Python: ${PYTHON_VER}"
    else
        fail "Python 3 is required. Install it first."
    fi




    if command -v git >/dev/null 2>&1; then
        GIT_VER=$(git --version | awk '{print $3}')
        ok "Git: ${GIT_VER}"
    else
        fail "Git is required. Install it first."
    fi



    if [[ "$OS" == "Linux" ]]; then
        RAM=$(free -h 2>/dev/null | awk '/^Mem:/{print $2}' || echo "Unknown")
        ok "RAM: ${RAM}"
    fi

    DISK_FREE=$(df -h . 2>/dev/null | awk 'NR==2{print $4}' || echo "Unknown")
    ok "Free Disk: ${DISK_FREE}"
}






get_kibo() {
    step "2/9" "Downloading Kibo"
    line

    INSTALL_DIR="${KIBO_DIR:-$HOME/kibo}"

    if [ -f "./pyproject.toml" ] && grep -q 'name = "kibo"' ./pyproject.toml 2>/dev/null; then
        INSTALL_DIR="$(pwd)"
        ok "Using current checkout: ${INSTALL_DIR}"
    fi

    if [ -d "$INSTALL_DIR" ]; then
        ok "Found existing installation: ${INSTALL_DIR}"
        cd "$INSTALL_DIR"
        if git pull --quiet 2>/dev/null; then
            ok "Updated to latest version"
        else
            warn "Using current version (update failed)"
        fi
    else
        info "Cloning to ${INSTALL_DIR}..."
        if git clone --depth 1 https://github.com/1dev-hridoy/Kibo.git "$INSTALL_DIR" 2>/dev/null; then
            cd "$INSTALL_DIR"
            ok "Cloned successfully"
        else
            fail "Clone failed. Check your internet connection."
        fi
    fi
}





setup_venv() {
    step "3/9" "Python Environment"
    line

    VENV="$INSTALL_DIR/venv"
    if [ ! -x "$VENV/bin/python" ]; then
        info "Creating virtual environment..."
        python3 -m venv "$VENV" || fail "Could not create venv"
        ok "Virtual environment created"
    else
        ok "Virtual environment exists"
    fi

    "$VENV/bin/pip" install --quiet --upgrade pip >/dev/null 2>&1 || true
    ok "pip updated"
}





install_package() {
    step "4/9" "Installing Kibo"
    line

    "$VENV/bin/pip" install --quiet -e . || fail "Installation failed"
    ok "Kibo package installed (editable mode)"
}




install_helpers() {
    step "5/9" "System Helpers"
    line

    PKG=""
    if command -v pacman >/dev/null 2>&1; then PKG="pacman"
    elif command -v apt-get >/dev/null 2>&1; then PKG="apt"
    elif command -v dnf >/dev/null 2>&1; then PKG="dnf"
    elif command -v zypper >/dev/null 2>&1; then PKG="zypper"
    elif command -v apk >/dev/null 2>&1; then PKG="apk"
    fi

    case "$PKG" in
        pacman)
            info "Installing via pacman..."
            sudo pacman -S --needed --noconfirm \
                libnotify brightnessctl wl-clipboard xclip espeak-ng scrot xdotool wmctrl python-tk python-pillow pulseaudio 2>/dev/null \
                && ok "Helpers installed (libnotify, brightnessctl, wl-clipboard, xclip, espeak-ng, scrot, xdotool, wmctrl)" \
                || warn "Some helpers failed (optional features may be limited)"
            ;;
        apt)
            info "Installing via apt..."
            sudo apt-get update -qq >/dev/null 2>&1 || true
            sudo apt-get install -y -qq \
                libnotify-bin brightnessctl wl-clipboard xclip espeak-ng scrot xdotool wmctrl python3-tk python3-venv pulseaudio-utils 2>/dev/null \
                && ok "Helpers installed" \
                || warn "Some helpers failed (optional features may be limited)"
            ;;
        dnf)
            info "Installing via dnf..."
            sudo dnf install -y -q \
                libnotify brightnessctl wl-clipboard xclip espeak-ng scrot xdotool wmctrl python3-tkinter pulseaudio-utils 2>/dev/null \
                && ok "Helpers installed" \
                || warn "Some helpers failed (optional features may be limited)"
            ;;
        zypper)
            info "Installing via zypper..."
            sudo zypper --non-interactive install -q \
                libnotify-tools brightnessctl wl-clipboard xclip espeak-ng scrot xdotool wmctrl python3-tk pulseaudio-utils 2>/dev/null \
                && ok "Helpers installed" \
                || warn "Some helpers failed (optional features may be limited)"
            ;;
        *)
            warn "No package manager found — install helpers manually if needed"
            info "Required: libnotify, brightnessctl, wl-clipboard, xclip, espeak-ng, scrot"
            ;;
    esac
}





select_model() {
    step "6/9" "AI Model Selection"
    line



    if [ -n "$MODEL_PRESET" ]; then
        case "$(printf '%s' "$MODEL_PRESET" | tr 'A-Z' 'a-z')" in
            needle|needle2|n) MODEL_CHOICE=1 ;;
            gemma|functiongemma|fg|google|func) MODEL_CHOICE=2 ;;
            both) MODEL_CHOICE=3 ;;
            qwen|qwen3|qwen3-0.6b|qwen-0.6b|qwen0.6b) MODEL_CHOICE=4 ;;
            qwen2.5-1.5b|qwen1.5b|qwen-1.5b) MODEL_CHOICE=5 ;;
            qwen2.5-3b|qwen3b|qwen-3b) MODEL_CHOICE=6 ;;
            gemma3|gemma3-1b|gemma-3-1b|gemma-1b|g3-1b) MODEL_CHOICE=7 ;;
            gemma3-4b|gemma-3-4b|gemma-4b|g3-4b) MODEL_CHOICE=8 ;;
            all) MODEL_CHOICE=9 ;;
            *) warn "Unknown --model '$MODEL_PRESET', using default Needle"; MODEL_CHOICE=1 ;;
        esac
        info "Model selected via --model: $MODEL_PRESET"
        return
    fi


    printf "\n"
    printf "  ${BOLD}┌─────────────────────────────────────────────────┐${NC}\n"
    printf "  ${BOLD}│${NC}  ${WHITE}Choose your AI model:${NC}                            ${BOLD}│${NC}\n"
    printf "  ${BOLD}├─────────────────────────────────────────────────┤${NC}\n"
    printf "  ${BOLD}│${NC}                                                 ${BOLD}│${NC}\n"
    printf "  ${BOLD}│${NC}  ${GREEN}[1]${NC} ${BOLD}Needle 2${NC}        ${YELLOW}14 MB${NC}   ${DIM}Fast, lightweight${NC}     ${BOLD}│${NC}\n"
    printf "  ${BOLD}│${NC}      ${DIM}by Cactus Compute${NC}                           ${BOLD}│${NC}\n"
    printf "  ${BOLD}│${NC}                                                 ${BOLD}│${NC}\n"
    printf "  ${BOLD}│${NC}  ${GREEN}[2]${NC} ${BOLD}FunctionGemma${NC}   ${YELLOW}253 MB${NC}  ${DIM}Smarter reasoning${NC}     ${BOLD}│${NC}\n"
    printf "  ${BOLD}│${NC}      ${DIM}by Google DeepMind${NC}                          ${BOLD}│${NC}\n"
    printf "  ${BOLD}│${NC}                                                 ${BOLD}│${NC}\n"
    printf "  ${BOLD}│${NC}  ${GREEN}[3]${NC} ${BOLD}Needle + Gemma${NC}  ${YELLOW}267 MB${NC}  ${DIM}Switch anytime${NC}        ${BOLD}│${NC}\n"
    printf "  ${BOLD}│${NC}                                                 ${BOLD}│${NC}\n"
    printf "  ${BOLD}│${NC}  ${GREEN}[4]${NC} ${BOLD}Qwen3 0.6B${NC}      ${YELLOW}397 MB${NC}  ${DIM}32k ctx${NC}               ${BOLD}│${NC}\n"
    printf "  ${BOLD}│${NC}  ${GREEN}[5]${NC} ${BOLD}Qwen2.5 1.5B${NC}    ${YELLOW}1.1 GB${NC}  ${DIM}Balanced${NC}              ${BOLD}│${NC}\n"
    printf "  ${BOLD}│${NC}  ${GREEN}[6]${NC} ${BOLD}Qwen2.5 3B${NC}      ${YELLOW}2.1 GB${NC}  ${DIM}Most capable Qwen${NC}     ${BOLD}│${NC}\n"
    printf "  ${BOLD}│${NC}  ${GREEN}[7]${NC} ${BOLD}Gemma 3 1B${NC}      ${YELLOW}806 MB${NC}  ${DIM}128k ctx${NC}               ${BOLD}│${NC}\n"
    printf "  ${BOLD}│${NC}  ${GREEN}[8]${NC} ${BOLD}Gemma 3 4B${NC}      ${YELLOW}2.5 GB${NC}  ${DIM}Most capable${NC}           ${BOLD}│${NC}\n"
    printf "  ${BOLD}│${NC}  ${GREEN}[9]${NC} ${BOLD}Download all${NC}    ${YELLOW}~9 GB${NC}  ${DIM}Everything${NC}             ${BOLD}│${NC}\n"
    printf "  ${BOLD}│${NC}                                                 ${BOLD}│${NC}\n"
    printf "  ${BOLD}└─────────────────────────────────────────────────┘${NC}\n"
    printf "\n"
    printf "  ${BOLD}Enter 1-9 [${GREEN}default: 1${NC}${BOLD}]: ${NC}"
    if [ -t 0 ]; then
        read -r MODEL_CHOICE
    else
        MODEL_CHOICE="1"
        printf "1 (piped install — default)\n"
        printf "  ${DIM}Tip: install a specific model with:${NC}\n"
        printf "  ${DIM}curl -sLO https://raw.githubusercontent.com/1dev-hridoy/Kibo/main/install.sh && ./install.sh --model qwen2.5-3b${NC}\n"
    fi
    MODEL_CHOICE="${MODEL_CHOICE:-1}"
}




download_models() {
    step "7/9" "Setting Up Models"
    line

    mkdir -p "$HOME/.agent_models/functiongemma"

    download_gguf() {
        local key="$1" repo="$2" file="$3" label="$4" size="$5"
        local dir="$HOME/.agent_models/$key"
        local path="$dir/$file"
        mkdir -p "$dir"
        if [ -f "$path" ]; then
            ok "$label already downloaded"
            return
        fi
        info "Downloading $label ($size)..."
        info "This may take a few minutes on slow connections."
        printf "\n"
        wget -q --show-progress -O "$path.part" \
            "https://huggingface.co/$repo/resolve/main/$file" \
            && mv "$path.part" "$path" && ok "$label downloaded" \
            || { rm -f "$path.part"; warn "$label download failed"; }
        printf "\n"
    }

    download_functiongemma() {
        download_gguf functiongemma \
            "unsloth/functiongemma-270m-it-GGUF" \
            "functiongemma-270m-it-Q4_K_M.gguf" \
            "FunctionGemma 270M" "253 MB"
    }



    download_qwen3_06b() {
        download_gguf qwen3-0.6b "unsloth/Qwen3-0.6B-GGUF" \
            "Qwen3-0.6B-Q4_K_M.gguf" "Qwen3 0.6B" "397 MB"
    }

    download_qwen25_15b() {
        download_gguf qwen2.5-1.5b "Qwen/Qwen2.5-1.5B-Instruct-GGUF" \
            "qwen2.5-1.5b-instruct-q4_k_m.gguf" "Qwen2.5 1.5B" "1.1 GB"
    }




    download_qwen25_3b() {
        download_gguf qwen2.5-3b "Qwen/Qwen2.5-3B-Instruct-GGUF" \
            "qwen2.5-3b-instruct-q4_k_m.gguf" "Qwen2.5 3B" "2.1 GB"
    }



    download_gemma3_1b() {
        download_gguf gemma3-1b "unsloth/gemma-3-1b-it-GGUF" \
            "gemma-3-1b-it-Q4_K_M.gguf" "Gemma 3 1B" "806 MB"
    }




    download_gemma3_4b() {
        download_gguf gemma3-4b "unsloth/gemma-3-4b-it-GGUF" \
            "gemma-3-4b-it-Q4_K_M.gguf" "Gemma 3 4B" "2.5 GB"
    }

    verify_needle() {
        "$VENV/bin/python" -c 'import needle' 2>/dev/null \
            && ok "Needle engine ready" \
            || warn "Needle not found"
    }

    install_llama_cpp() {
        "$VENV/bin/pip" install --quiet llama-cpp-python 2>/dev/null \
            && ok "llama-cpp-python installed" \
            || warn "llama-cpp-python install failed"
    }

    set_active() {
        echo "{\"active_model\": \"$1\"}" > "$HOME/.agent_model_config.json"
    }

    case "$MODEL_CHOICE" in
        1)
            verify_needle
            set_active needle
            ok "Default model: Needle 2"
            ;;
        2)
            download_functiongemma
            install_llama_cpp
            set_active functiongemma
            ok "Default model: FunctionGemma"
            ;;
        3)
            verify_needle
            download_functiongemma
            install_llama_cpp
            set_active needle
            ok "Default model: Needle 2"
            info "Type 'gemma' to switch to FunctionGemma"
            ;;
        4)
            install_llama_cpp
            download_qwen3_06b
            set_active qwen3-0.6b
            ok "Default model: Qwen3 0.6B"
            ;;
        5)



            install_llama_cpp
            download_qwen25_15b
            set_active qwen2.5-1.5b
            ok "Default model: Qwen2.5 1.5B"
            ;;



        6)
            install_llama_cpp
            download_qwen25_3b
            set_active qwen2.5-3b
            ok "Default model: Qwen2.5 3B"
            ;;



        7)
            install_llama_cpp
            download_gemma3_1b
            set_active gemma3-1b
            ok "Default model: Gemma 3 1B"
            ;;
        8)

        
            install_llama_cpp
            download_gemma3_4b
            set_active gemma3-4b
            ok "Default model: Gemma 3 4B"
            ;;
        9)
            verify_needle
            install_llama_cpp
            download_functiongemma
            download_qwen3_06b
            download_qwen25_15b
            download_qwen25_3b
            download_gemma3_1b
            download_gemma3_4b
            set_active needle
            ok "Default model: Needle 2"
            info "Type 'models' to see and switch between all downloaded models"
            ;;
        *)
            verify_needle
            download_functiongemma
            install_llama_cpp
            set_active needle
            ;;
    esac
}




allow_chat() {
    local chat_id="$1"
    local label="$2"
    if KIBO_CHAT_ID="$chat_id" "$VENV/bin/python" -c '
import os
from agent.telegram.auth import add_allowed
add_allowed(int(os.environ["KIBO_CHAT_ID"]))
' >/dev/null 2>&1; then
        ok "${label} ${chat_id} allowed"
    else
        warn "Could not save ${chat_id} — add it later with /allow <chat_id>"
    fi
}


setup_telegram() {
    step "8/9" "Telegram Chats"
    line

    printf "\n"
    printf "  ${DIM}Which chats may drive this PC?${NC}\n"
    printf "  ${DIM}Group ids look like -1001234567890. Your own id comes from /chatid in the bot.${NC}\n"
    printf "\n"

    local any_id=0

    local group_id=""
    if [ -t 0 ]; then
        printf "  ${BOLD}Group chat id${NC} [${DIM}press Enter to skip${NC}${BOLD}]: ${NC}"
        read -r group_id
    else
        read -r group_id || group_id=""
        group_id="${group_id:-${KIBO_GROUP_ID:-}}"
    fi

    if printf "%s" "$group_id" | grep -qE '^-?[0-9]+$'; then
        allow_chat "$group_id" "Group"
        any_id=1
    else
        info "No group id — you can add one later with /allow <chat_id>"
    fi

    local user_id=""
    if [ -t 0 ]; then
        printf "  ${BOLD}Your user id for DM${NC} [${DIM}press Enter to skip${NC}${BOLD}]: ${NC}"
        read -r user_id
    else
        read -r user_id || user_id=""
        user_id="${user_id:-${KIBO_USER_ID:-}}"
    fi

    if printf "%s" "$user_id" | grep -qE '^-?[0-9]+$'; then
        allow_chat "$user_id" "User"
        any_id=1
    else
        info "No user id — the first chat to message the bot becomes the owner"
    fi

    printf "\n"
    if [ "$any_id" = "1" ]; then
        ok "Allowed chats stored in ~/.config/kibo/telegram_allowed.json"
    else
        warn "No chats set — message the bot once, it locks you in as owner"
    fi
    line
}


write_kibo_cli() {
    local bin_dir="$HOME/.local/bin"
    mkdir -p "$bin_dir"

    cat > "$bin_dir/kibo" <<CLIEOF
#!/usr/bin/env bash

KIBO_HOME="\${KIBO_HOME:-$INSTALL_DIR}"
export KIBO_HOME

exec "\${KIBO_PY:-$INSTALL_DIR/venv/bin/python}" "$INSTALL_DIR/agent/kibo_cli.py" "\$@"
CLIEOF

    chmod +x "$bin_dir/kibo"

    if case ":$PATH:" in *":$bin_dir:"*) true ;; *) false ;; esac; then
        ok "Global command installed: kibo"
    else
        for rc in "$HOME/.bashrc" "$HOME/.zshrc" "$HOME/.profile"; do
            [ -f "$rc" ] || touch "$rc"
            grep -q '.local/bin' "$rc" 2>/dev/null \
                || printf '\nexport PATH="$HOME/.local/bin:$PATH"\n' >> "$rc"
        done
        ok "Global command installed: kibo (added ${bin_dir} to PATH)"
    fi
}


install_cli() {
    step "9/9" "Global Command"
    line
    write_kibo_cli
    line
}


verify_install() {
    printf "\n"
    step "✓" "Verification"
    line

    TOOL_COUNT=$("$VENV/bin/python" -c 'from agent.tools import ALL_TOOLS; print(len(ALL_TOOLS))' 2>/dev/null) \
        || fail "Installation verification failed"
    ok "Kibo is ready — ${TOOL_COUNT} tools registered"

    printf "\n"
    printf "  ${BOLD}${GREEN}╔══════════════════════════════════════════════════╗${NC}\n"
    printf "  ${BOLD}${GREEN}║${NC}            ${BOLD}${GREEN}Installation Complete!${NC}               ${BOLD}${GREEN}║${NC}\n"
    printf "  ${BOLD}${GREEN}╚══════════════════════════════════════════════════╝${NC}\n"
    printf "\n"
    printf "  ${BOLD}Quick Start:${NC}\n\n"
    printf "    ${CYAN}kibo${NC}                  ${DIM}show every command${NC}\n"
    printf "    ${CYAN}kibo chat${NC}            ${DIM}terminal chat${NC}\n"
    printf "    ${CYAN}kibo web${NC}             ${DIM}browser UI (localhost:5000)${NC}\n"
    printf "    ${CYAN}kibo telegram${NC}       ${DIM}telegram bot${NC}\n"
    printf "    ${CYAN}kibo status${NC}         ${DIM}what is running${NC}\n"
    printf "\n"
    printf "  ${BOLD}Or from the project folder:${NC}\n\n"
    printf "    ${CYAN}cd ${INSTALL_DIR}${NC}\n"
    printf "    ${CYAN}./run.sh${NC}              ${DIM}# terminal chat${NC}\n"
    printf "    ${CYAN}./run.sh web${NC}          ${DIM}# browser UI${NC}\n"
    printf "    ${CYAN}./run.sh telegram${NC}     ${DIM}# telegram bot${NC}\n"
    printf "\n"
    printf "  ${BOLD}Try these commands:${NC}\n\n"
    printf "    ${DIM}ls${NC}                    list files\n"
    printf "    ${DIM}battery${NC}               check battery\n"
    printf "    ${DIM}volume 80${NC}             set volume\n"
    printf "    ${DIM}screenshot${NC}            take screenshot\n"
    printf "    ${DIM}open firefox${NC}          launch app\n"
    printf "    ${DIM}models${NC}                switch AI models\n"
    printf "\n"
    printf "  ${DIM}Docs: https://github.com/1dev-hridoy/Kibo${NC}\n"
    printf "  ${DIM}License: MIT${NC}\n\n"
}




parse_args() {
    while [ $# -gt 0 ]; do
        case "$1" in
            --model)
                shift
                MODEL_PRESET="${1:-}"
                ;;
            --model=*)
                MODEL_PRESET="${1#*=}"
                ;;
            --fresh)
                : # accepted for backwards compatibility
                ;;
        esac
        shift
    done
}


main() {
    parse_args "$@"
    show_banner
    check_system
    get_kibo
    setup_venv
    install_package
    install_helpers
    select_model
    download_models
    setup_telegram
    install_cli
    verify_install
}

main "$@"
