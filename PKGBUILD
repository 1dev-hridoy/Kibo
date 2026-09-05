# Maintainer: 1dev-hridoy <https://github.com/1dev-hridoy>
# Upstream:    https://github.com/1dev-hridoy/MobileAgent
#
# Build & install:
#   makepkg -si
#
# This PKGBUILD installs the Agent system-wide as a Python package
# (via pip inside a staged prefix). For a user-local, venv-based install
# prefer ./install.sh instead.

pkgname=agent-desktop
pkgver=3.0.0
pkgrel=1
pkgdesc="Agent — AI desktop assistant for PCs (Arch packaging): natural-language control powered by the 14MB Needle LLM"
arch=(any)
url="https://github.com/1dev-hridoy/MobileAgent"
license=(MIT)
depends=(
    python
    python-flask
    python-pydantic
    python-waitress
    libnotify
    brightnessctl
    xdg-utils
)
optdepends=(
    'python-pytelegrambotapi: Telegram remote control'
    'wl-clipboard: clipboard on Wayland'
    'xclip: clipboard on X11'
    'espeak-ng: text-to-speech'
    'ffmpeg: webcam capture'
    'networkmanager: WiFi info & scanning (nmcli)'
    'scrot: screenshots on X11'
    'pipewire-audio: volume control & mic recording (pactl/pw-record)'
)
makedepends=(python-setuptools python-build python-installer python-wheel)
provides=(agent)
conflicts=(agent)
source=("$pkgname-$pkgver.tar.gz::https://github.com/1dev-hridoy/MobileAgent/archive/refs/tags/v$pkgver.tar.gz")
sha256sums=('SKIP')

build() {
    cd "$srcdir/MobileAgent-$pkgver/harness-arch" 2>/dev/null \
        || cd "$srcdir/../harness-arch"
    python -m build --wheel --no-isolation
}

package() {
    cd "$srcdir/MobileAgent-$pkgver/harness-arch" 2>/dev/null \
        || cd "$srcdir/../harness-arch"
    python -m installer --destdir="$pkgdir" dist/*.whl
    install -Dm644 LICENSE "$pkgdir/usr/share/licenses/$pkgname/LICENSE" 2>/dev/null || true
}