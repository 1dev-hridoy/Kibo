"""
Network & system tools — cross-platform: WiFi info & scan (nmcli /
airport / netsh), downloads (wget/curl/Invoke-WebRequest), system info,
web search & RAG content extraction.
"""

import needle
from agent.runner import (
    wifi_info, wifi_scan, system_info, has_internet,
    download_file as _download,
    web_search_and_extract, fetch_url_text,
)


def _kv(d):
    """Dict → 'Key: value' lines, None values skipped."""
    lines = []
    for k, v in d.items():
        if v is None:
            continue
        name = k.replace("_", " ").capitalize()
        lines.append(f"{name}: {v}")
    return "\n".join(lines)


@needle.tool
def get_wifi_info():
    """Get details of the active network connection (SSID, IP, signal)."""
    print("[Tool] get_wifi_info()")
    info = wifi_info()
    if not info.get("connected"):
        return "This PC is not connected to any network."
    medium = info.get("medium") or "wifi"
    if medium == "ethernet":
        return (f"Connected via ethernet — IP {info.get('ip')}. "
                "No WiFi interface in use.")
    ssid = info.get("ssid") or "unknown network"
    sig = info.get("signal")
    sig_s = f", signal {sig}%" if sig is not None else ""
    return f"Connected to WiFi '{ssid}' — IP {info.get('ip')}{sig_s}."


@needle.tool
def scan_wifi_networks():
    """Scan for nearby WiFi networks and their signal strengths."""
    print("[Tool] scan_wifi_networks()")
    nets = wifi_scan()
    if not nets:
        return "No WiFi networks found (or no WiFi adapter present)."
    rows = []
    for n in nets[:12]:
        ssid = n.get("ssid") or "(hidden)"
        sig = n.get("signal")
        rows.append(f"{ssid} ({sig}%)" if sig is not None else ssid)
    return f"{len(nets)} networks found: " + ", ".join(rows) + "."


@needle.tool
def download_file(url: str, title: str = "Download"):
    """Download a file from a URL to your Downloads folder."""
    print(f"[Tool] download_file('{url}', '{title}')")
    return _download(url, title)


@needle.tool
def get_system_info():
    """Get host system information (OS, hostname, architecture, IP)."""
    print("[Tool] get_system_info()")
    body = _kv(system_info())
    return body or "Couldn't read system information."


@needle.tool
def check_internet():
    """Check if this PC has an active internet connection."""
    print("[Tool] check_internet()")
    return "Connected to the internet." if has_internet() else "No internet connection detected."


@needle.tool
def web_search(query: str) -> str:
    """Search the web using DuckDuckGo and return results with content.
    Use for: finding current information, documentation, news, or any web content.
    Automatically fetches content from top results for deeper context (RAG)."""
    print(f"[Tool] web_search('{query}')")
    return web_search_and_extract(query, max_results=5, fetch_top=2)


@needle.tool
def fetch_url(url: str) -> str:
    """Fetch content from a URL and return clean text (HTML stripped).
    Use for: reading articles, documentation, API responses, or any web page."""
    print(f"[Tool] fetch_url('{url}')")
    return fetch_url_text(url, max_chars=8000)
