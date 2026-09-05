"""
App launcher tools — cross-platform: native apps (per-OS launcher maps
in config) plus any web app via the default browser.
"""

import os
import needle
from agent.runner import launch, open_url, open_path, list_files as _list_files, list_installed_apps as _list_apps
from agent.config_apps import APP_URLS


@needle.tool
def open_app(name: str):
    """
    Open an app, URL, or file on this PC.
    Supports: calculator, settings, files, terminal, notepad, code/vscode,
    firefox, whatsapp, youtube, chrome, instagram, spotify, telegram,
    facebook, twitter/x, gmail, maps — or any http(s) URL or local file
    path.
    """
    print(f"[Tool] open_app('{name}')")
    raw = name.strip()
    clean = raw.lower().replace("open ", "").replace("the ", "").strip()

    # Direct URL
    if raw.lower().startswith(("http://", "https://")):
        open_url(raw)
        return f"Opened URL: {raw}"

    # Direct file path
    if os.path.exists(raw):
        return open_path(raw)

    # Known app / web app
    result = launch(clean)
    if result.startswith(("Success", "Opened")):
        return result

    # Fuzzy match against the URL database before giving up
    for key in APP_URLS:
        if key in clean or clean in key:
            open_url(APP_URLS[key])
            return f"Opened: {key}"

    return result


@needle.tool
def open_local_path(path: str):
    """
    Open a local file or folder on this PC with the default handler.
    """
    print(f"[Tool] open_local_path('{path}')")
    return open_path(path)


@needle.tool
def list_files(path: str = ""):
    """
    List files and folders in a directory. Defaults to home directory.
    Shows names, types (file/dir), and sizes.
    """
    print(f"[Tool] list_files('{path}')")
    result = _list_files(path)
    if "error" in result:
        return result["error"]
    items = result.get("items", [])
    if not items:
        return f"Empty directory: {result.get('path', path)}"
    lines = [f"Contents of {result.get('path', path)}:"]
    for item in items[:50]:
        icon = "[DIR] " if item["type"] == "dir" else "      "
        size = f" ({item['size']} bytes)" if item["type"] == "file" and item["size"] else ""
        lines.append(f"  {icon}{item['name']}{size}")
    if result.get("total", 0) > 50:
        lines.append(f"  ... and {result['total'] - 50} more items")
    return "\n".join(lines)


@needle.tool
def list_installed_apps():
    """
    List installed software on this PC.
    Shows app names and versions.
    """
    print("[Tool] list_installed_apps()")
    apps = _list_apps()
    if not apps:
        return "Couldn't retrieve installed applications on this system."
    lines = [f"Found {len(apps)} installed applications:"]
    for app in apps[:80]:
        ver = f" v{app['version']}" if app.get("version") else ""
        lines.append(f"  - {app['name']}{ver}")
    if len(apps) > 80:
        lines.append(f"  ... and {len(apps) - 80} more")
    return "\n".join(lines)
