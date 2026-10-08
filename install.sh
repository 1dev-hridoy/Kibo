#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════════════
#  Kibo — One-line Installer
#  Usage: curl -sL https://raw.githubusercontent.com/1dev-hridoy/Kibo/main/install.sh | bash
# ═══════════════════════════════════════════════════════════════════════
set -e





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
    step "1/7" "System Check"
    line

    # OS
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

    # Disk
    DISK_FREE=$(df -h . 2>/dev/null | awk 'NR==2{print $4}' || echo "Unknown")
    ok "Free Disk: ${DISK_FREE}"
}






get_kibo() {
    step "2/7" "Downloading Kibo"
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
    step "3/7" "Python Environment"
    line

    VENV="$INSTALL_DIR/venv"
    if [ ! -x "$VENV/bin/python" ]; then
        info "Creating virtual environment..."
        python3 -m venv "$VENV" || fail "Could not create venv"
        ok "Virtual environment created"
    else
        ok "Virtual environment exists"
    fi

    # Upgrade pip
    "$VENV/bin/pip" install --quiet --upgrade pip >/dev/null 2>&1 || true
    ok "pip updated"
}





install_package() {
    step "4/7" "Installing Kibo"
    line

    "$VENV/bin/pip" install --quiet -e . || fail "Installation failed"
    ok "Kibo package installed (editable mode)"
}




install_helpers() {
    step "5/7" "System Helpers"
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
    step "6/7" "AI Model Selection"
    line

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
    printf "  ${BOLD}│${NC}  ${GREEN}[3]${NC} ${BOLD}Both models${NC}     ${YELLOW}267 MB${NC}  ${DIM}Switch anytime${NC}        ${BOLD}│${NC}\n"
    printf "  ${BOLD}│${NC}      ${DIM}Recommended for full experience${NC}             ${BOLD}│${NC}\n"
    printf "  ${BOLD}│${NC}                                                 ${BOLD}│${NC}\n"
    printf "  ${BOLD}└─────────────────────────────────────────────────┘${NC}\n"
    printf "\n"
    printf "  ${BOLD}Enter 1, 2, or 3 [${GREEN}default: 1${NC}${BOLD}]: ${NC}"
    if [ -t 0 ]; then
        read -r MODEL_CHOICE
    else
        MODEL_CHOICE="1"
        printf "1 (piped install — default)\n"
        printf "  ${DIM}Tip: download and run directly for model selection:${NC}\n"
        printf "  ${DIM}curl -sLO https://raw.githubusercontent.com/1dev-hridoy/Kibo/main/install.sh && ./install.sh${NC}\n"
    fi
    MODEL_CHOICE="${MODEL_CHOICE:-1}"
}




download_models() {
    step "7/7" "Setting Up Models"
    line

    mkdir -p "$HOME/.agent_models/functiongemma"

    download_functiongemma() {
        MODEL_PATH="$HOME/.agent_models/functiongemma/functiongemma-270m-it-Q4_K_M.gguf"
        if [ -f "$MODEL_PATH" ]; then
            ok "FunctionGemma already downloaded"
            return
        fi
        info "Downloading FunctionGemma 270M (~253 MB)..."
        info "This may take a few minutes on slow connections."
        printf "\n"
        wget -q --show-progress -O "$MODEL_PATH" \
            "https://huggingface.co/unsloth/functiongemma-270m-it-GGUF/resolve/main/functiongemma-270m-it-Q4_K_M.gguf" \
            && ok "FunctionGemma downloaded" \
            || warn "Download failed — you can still use Needle"
        printf "\n"
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

    case "$MODEL_CHOICE" in
        1)
            verify_needle
            echo '{"active_model": "needle"}' > "$HOME/.agent_model_config.json"
            ok "Default model: Needle 2"
            ;;
        2)
            download_functiongemma
            install_llama_cpp
            echo '{"active_model": "functiongemma"}' > "$HOME/.agent_model_config.json"
            ok "Default model: FunctionGemma"
            ;;
        3)
            verify_needle
            download_functiongemma
            install_llama_cpp
            echo '{"active_model": "needle"}' > "$HOME/.agent_model_config.json"
            ok "Default model: Needle 2"
            info "Type 'gemma' to switch to FunctionGemma"
            ;;
        *)
            verify_needle
            download_functiongemma
            install_llama_cpp
            echo '{"active_model": "needle"}' > "$HOME/.agent_model_config.json"
            ;;
    esac
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
    printf "    ${CYAN}cd ${INSTALL_DIR}${NC}\n"
    printf "    ${CYAN}./run.sh${NC}              ${DIM}# terminal chat${NC}\n"
    printf "    ${CYAN}./run.sh web${NC}          ${DIM}# browser UI (localhost:5000)${NC}\n"
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




main() {
    show_banner
    check_system
    get_kibo
    setup_venv
    install_package
    install_helpers
    select_model
    download_models
    verify_install
}

main "$@"
