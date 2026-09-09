"""
Security auditing — ARP spoofing detection, VPN connection audit,
and website security header/SSL auditing.
"""

import json
import os
import re
import socket
import ssl
import subprocess
import urllib.parse
import urllib.request





def detect_arp_spoofing() -> dict:
    """Inspect ARP cache for signs of MITM/ARP spoofing attacks.

    Detects when multiple IP addresses map to the same MAC address,
    which is a strong indicator of ARP spoofing.

    Returns dict with 'suspicious' (bool), 'entries', 'alerts'.
    """
    entries = []
    alerts = []


    try:
        arp_file = "/proc/net/arp"
        if os.path.exists(arp_file):
            with open(arp_file) as f:
                for line in f.readlines()[1:]:
                    parts = line.split()
                    if len(parts) >= 4:
                        entries.append({
                            "ip": parts[0],
                            "mac": parts[3],
                            "interface": parts[5] if len(parts) > 5 else "",
                        })


                
        else:
            res = subprocess.run(
                ["arp", "-a"],
                capture_output=True, text=True, timeout=10, errors="replace")
            for line in res.stdout.splitlines():
                match = re.search(
                    r"(\d+\.\d+\.\d+\.\d+)\s+.*?([\da-fA-F]{1,2}[:-]){5}", line)
                if match:
                    entries.append({
                        "ip": match.group(1),
                        "mac": line.split()[3] if len(line.split()) > 3 else "",
                        "interface": "",
                    })
    except (OSError, FileNotFoundError):
        pass





    mac_to_ips = {}
    for entry in entries:
        mac = entry["mac"].lower()
        if mac and mac != "00:00:00:00:00:00" and mac != "ff:ff:ff:ff:ff:ff":
            mac_to_ips.setdefault(mac, []).append(entry["ip"])

    for mac, ips in mac_to_ips.items():
        if len(ips) > 1:
            alerts.append(
                f"ALERT: MAC {mac} maps to {len(ips)} IPs: {', '.join(ips)}")

    return {
        "suspicious": len(alerts) > 0,
        "entries": entries[:30],
        "alerts": alerts,
    }





_VPN_KEYWORDS = [
    "vpn", "proxy", "tor", "tunnel", "nord", "express",
    "surfshark", "mullvad", "proton", "wireguard",
]


def audit_vpn_connection() -> dict:
    """Check public IP, ISP, and detect VPN/proxy/Tor leaks.

    Returns dict with 'public_ip', 'isp', 'country', 'vpn_likely', 'details'.
    """
    result = {
        "public_ip": "", "isp": "", "country": "",
        "vpn_likely": False, "details": [],
    }

    try:
        req = urllib.request.Request(
            "http://ip-api.com/json/?fields=query,isp,country,org,as",
            headers={"User-Agent": "Kibo/1.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())

        result["public_ip"] = data.get("query", "")
        result["isp"] = data.get("isp", "")
        result["country"] = data.get("country", "")
        result["org"] = data.get("org", "")
        result["as"] = data.get("as", "")

        org_lower = (data.get("org", "") + " " + data.get("isp", "")).lower()
        for kw in _VPN_KEYWORDS:
            if kw in org_lower:
                result["vpn_likely"] = True
                result["details"].append(f"ISP/org contains VPN keyword: '{kw}'")

    except Exception as e:
        result["details"].append(f"Error checking public IP: {e}")

    return result





_SECURITY_HEADERS = {
    "Strict-Transport-Security": "HSTS",
    "Content-Security-Policy": "CSP",
    "X-Frame-Options": "X-Frame-Options",
    "X-Content-Type-Options": "X-Content-Type-Options",
    "X-XSS-Protection": "X-XSS-Protection",
    "Referrer-Policy": "Referrer-Policy",
    "Permissions-Policy": "Permissions-Policy",
}


def _audit_ssl(hostname: str, port: int) -> dict:
    """Check SSL certificate validity and expiry."""
    ssl_info = {}
    try:
        ctx = ssl.create_default_context()
        with socket.create_connection((hostname, port), timeout=10) as sock:
            with ctx.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()
                ssl_info["subject"] = dict(x[0] for x in cert.get("subject", []))
                ssl_info["issuer"] = dict(x[0] for x in cert.get("issuer", []))
                ssl_info["version"] = cert.get("version", "")
                ssl_info["serial"] = cert.get("serialNumber", "")

                not_after = cert.get("notAfter", "")
                ssl_info["expires"] = not_after
                if not_after:
                    from datetime import datetime
                    try:
                        exp = datetime.strptime(not_after, "%b %d %H:%M:%S %Y %Z")
                        ssl_info["days_until_expiry"] = (exp - datetime.utcnow()).days
                    except ValueError:
                        pass
    except ssl.SSLCertVerificationError as e:
        ssl_info["error"] = str(e)
    except Exception as e:
        ssl_info["error"] = str(e)

    return ssl_info


def _audit_headers(url: str) -> tuple[dict, list[str]]:
    """Check HTTP security headers. Returns (present_headers, missing_headers)."""
    present = {}
    missing = []

    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "Kibo/1.0",
            "Accept": "text/html",
        })
        with urllib.request.urlopen(req, timeout=10) as resp:
            headers = dict(resp.headers)

            for header, name in _SECURITY_HEADERS.items():
                found = False
                for k, v in headers.items():
                    if k.lower() == header.lower():
                        present[name] = v
                        found = True
                        break
                if not found:
                    missing.append(name)

            server = headers.get("Server", "")
            if server:
                present["Server"] = server

    except Exception as e:
        present["error"] = str(e)

    return present, missing








def audit_website_security(url: str) -> dict:
    """Audit a website's SSL certificate and HTTP security headers.

    Returns dict with 'ssl' info, 'headers' audit, 'grade' (A-F).
    """
    if not url.startswith("http"):
        url = "https://" + url

    parsed = urllib.parse.urlparse(url)
    hostname = parsed.hostname or ""
    port = parsed.port or 443

    ssl_info = _audit_ssl(hostname, port)
    present, missing = _audit_headers(url)

    # Grade
    if ssl_info.get("error"):
        grade = "F"
    elif len(missing) == 0:
        grade = "A"
    elif len(missing) <= 2:
        grade = "B"
    elif len(missing) <= 4:
        grade = "C"
    else:
        grade = "D"

    return {
        "url": url,
        "ssl": ssl_info,
        "headers": present,
        "missing_headers": missing,
        "grade": grade,
    }
