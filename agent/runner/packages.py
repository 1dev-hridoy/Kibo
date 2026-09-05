"""Package management: package_install(), package_uninstall()."""

import shutil

from agent.config import IS_WINDOWS, IS_MACOS, IS_LINUX
from agent.runner.common import run


def package_install(name: str) -> str:
    """Install a package using the system package manager."""
    if IS_LINUX:
        if shutil.which("pacman"):
            return run(["sudo", "pacman", "-S", "--needed", "--noconfirm", name], timeout=120)
        elif shutil.which("apt"):
            return run(["sudo", "apt-get", "install", "-y", name], timeout=120)
        elif shutil.which("dnf"):
            return run(["sudo", "dnf", "install", "-y", name], timeout=120)
        elif shutil.which("zypper"):
            return run(["sudo", "zypper", "--non-interactive", "install", name], timeout=120)
        return "No supported package manager found."
    elif IS_MACOS:
        if shutil.which("brew"):
            return run(["brew", "install", name], timeout=120)
        return "Homebrew not installed."
    elif IS_WINDOWS:
        if shutil.which("winget"):
            return run(["winget", "install", "--id", name, "--accept-package-agreements"], timeout=120)
        return "winget not available."
    return "Package management not supported."


def package_uninstall(name: str) -> str:
    """Uninstall a package using the system package manager."""
    if IS_LINUX:
        if shutil.which("pacman"):
            return run(["sudo", "pacman", "-Rns", "--noconfirm", name], timeout=60)
        elif shutil.which("apt"):
            return run(["sudo", "apt-get", "remove", "-y", name], timeout=60)
        elif shutil.which("dnf"):
            return run(["sudo", "dnf", "remove", "-y", name], timeout=60)
        return "No supported package manager found."
    elif IS_MACOS:
        if shutil.which("brew"):
            return run(["brew", "uninstall", name], timeout=60)
        return "Homebrew not installed."
    elif IS_WINDOWS:
        if shutil.which("winget"):
            return run(["winget", "uninstall", "--id", name], timeout=60)
        return "winget not available."
    return "Package management not supported."
