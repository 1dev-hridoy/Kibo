"""
Security audit tool wrappers — ARP, VPN, website, DNS, WHOIS, geolocation, subdomain.
"""

import needle

from agent.runner.security_audit import (
    detect_arp_spoofing as _arp_check,
    audit_vpn_connection as _vpn_audit,
    audit_website_security as _web_audit,
)
from agent.runner.dns_intel import (
    dns_lookup as _dns,
    whois_lookup as _whois,
    ip_geolocation_lookup as _geo,
    check_subdomain_takeover as _subdomain_check,
)






@needle.tool
def detect_arp_spoofing() -> str:
    """Check for ARP spoofing / Man-in-the-Middle attacks on your network.
    Inspects the ARP cache for duplicate MAC addresses mapping to
    multiple IPs, which indicates active network interception."""
    print("[Tool] detect_arp_spoofing()")
    result = _arp_check()
    alerts = result.get("alerts", [])
    entries = result.get("entries", [])

    lines = [f"ARP table: {len(entries)} entries"]
    if alerts:
        lines.append("\n🚨 SECURITY ALERTS:")
        for a in alerts:
            lines.append(f"  ⚠ {a}")
    else:
        lines.append("\n✓ No ARP spoofing detected.")

    return "\n".join(lines)







@needle.tool
def audit_vpn_connection() -> str:
    """Audit your current VPN/proxy connection status.
    Checks public IP, ISP, and detects if traffic might be
    leaking through a VPN, proxy, or Tor exit node."""
    print("[Tool] audit_vpn_connection()")
    result = _vpn_audit()
    lines = ["VPN Connection Audit:"]
    lines.append(f"  Public IP: {result.get('public_ip', 'unknown')}")
    lines.append(f"  ISP: {result.get('isp', 'unknown')}")
    lines.append(f"  Country: {result.get('country', 'unknown')}")
    org = result.get("org", "")
    if org:


        lines.append(f"  Org: {org}")





    if result.get("vpn_likely"):
        lines.append("\n⚠ VPN/Proxy detected in ISP/org info.")
    else:
        lines.append("\n✓ No VPN/proxy indicators found in public IP info.")

    for detail in result.get("details", []):
        lines.append(f"  ℹ {detail}")

    return "\n".join(lines)





@needle.tool
def audit_website_security(url: str) -> str:
    """Audit a website's SSL certificate and HTTP security headers.
    Checks: HSTS, CSP, X-Frame-Options, X-Content-Type-Options,
    X-XSS-Protection, Referrer-Policy, SSL expiry, and server leakage.
    Returns a security grade (A-F)."""
    print(f"[Tool] audit_website_security('{url}')")
    result = _web_audit(url)

    lines = [f"Website Security Audit: {url}"]
    lines.append(f"  Grade: {result.get('grade', '?')}\n")




    ssl_info = result.get("ssl", {})
    if ssl_info.get("error"):
        lines.append(f"  SSL Error: {ssl_info['error']}")
    elif ssl_info.get("subject"):
        lines.append("  SSL Certificate:")
        subject = ssl_info.get("subject", {})
        cn = subject.get("commonName", "")
        if cn:
            lines.append(f"    Subject: {cn}")
        expires = ssl_info.get("expires", "")
        if expires:
            days = ssl_info.get("days_until_expiry", "?")
            lines.append(f"    Expires: {expires} ({days} days left)")




    headers = result.get("headers", {})
    if headers:
        lines.append("\n  Security Headers:")
        for name, value in headers.items():
            if name != "error":
                val_display = value[:60] + "..." if len(str(value)) > 60 else value
                lines.append(f"    ✓ {name}: {val_display}")

    missing = result.get("missing_headers", [])
    if missing:
        lines.append("\n  Missing Headers:")
        for h in missing:
            lines.append(f"    ✗ {h}")

    return "\n".join(lines)





@needle.tool
def dns_lookup(domain: str, record_type: str = "A") -> str:
    """Query DNS records for a domain using Cloudflare DNS-over-HTTPS.
    Use for: checking A, AAAA, MX, TXT, CNAME, NS records.
    Useful for debugging DNS issues or verifying domain configuration."""
    print(f"[Tool] dns_lookup('{domain}', '{record_type}')")
    result = _dns(domain, record_type)
    records = result.get("records", [])
    error = result.get("error")

    if error:
        return f"DNS lookup failed for {domain}: {error}"

    if not records:
        return f"No {record_type} records found for {domain}."

    lines = [f"DNS {record_type} records for {domain}:"]
    for r in records:
        lines.append(f"  {r['data']} (TTL: {r['ttl']}s)")


    return "\n".join(lines)




@needle.tool
def whois_lookup(domain: str) -> str:
    """Look up domain registration information via RDAP.
    Returns: registrar, creation date, expiration date, status."""
    print(f"[Tool] whois_lookup('{domain}')")
    result = _whois(domain)

    if result.get("error"):
        return f"WHOIS lookup failed for {domain}: {result['error']}"

    lines = [f"Domain: {result.get('name', domain)}"]
    if result.get("registrar"):
        lines.append(f"  Registrar: {result['registrar']}")
    if result.get("creation_date"):
        lines.append(f"  Created: {result['creation_date']}")
    if result.get("expiry_date"):
        lines.append(f"  Expires: {result['expiry_date']}")
    if result.get("updated_date"):
        lines.append(f"  Updated: {result['updated_date']}")
    status = result.get("status", [])
    if status:
        lines.append(f"  Status: {', '.join(status[:3])}")
    return "\n".join(lines)




@needle.tool
def ip_geolocation_lookup(ip: str) -> str:
    """Look up geographic location and ISP for an IP address.
    Returns: country, city, coordinates, ISP, and proxy/hosting detection."""
    print(f"[Tool] ip_geolocation_lookup('{ip}')")
    result = _geo(ip)

    if result.get("error"):
        return f"Geolocation failed for {ip}: {result['error']}"

    lines = [f"IP: {result.get('ip', ip)}"]
    lines.append(f"  Location: {result.get('city', '')}, {result.get('region', '')}, {result.get('country', '')}")
    lines.append(f"  Coordinates: {result.get('lat', 0)}, {result.get('lon', 0)}")
    lines.append(f"  ISP: {result.get('isp', '')}")
    org = result.get("org", "")
    if org:
        lines.append(f"  Org: {org}")
    if result.get("proxy"):
        lines.append("  ⚠ Proxy detected")
    if result.get("hosting"):
        lines.append("  ℹ Hosting/datacenter IP")
    return "\n".join(lines)







@needle.tool
def check_subdomain_takeover(domain: str) -> str:
    """Check if any subdomains of a domain are vulnerable to takeover.
    Scans common subdomains for dangling CNAME records pointing to
    unclaimed cloud resources (AWS, Azure, Heroku, GitHub, etc.)."""
    print(f"[Tool] check_subdomain_takeover('{domain}')")
    result = _subdomain_check(domain)

    vulnerable = result.get("vulnerable", [])
    total = len(result.get("safe", [])) + len(vulnerable)

    lines = [f"Scanned {total} subdomains of {domain}"]

    if vulnerable:
        lines.append(f"\n🚨 {len(vulnerable)} VULNERABLE subdomains:")
        for v in vulnerable:
            lines.append(f"  {v['subdomain']} → CNAME: {v['cname']}")
            lines.append(f"    Provider: {v.get('provider', 'unknown')} ⚠ TAKEOVER RISK")
    else:
        lines.append("\n✓ No vulnerable subdomains found.")

    return "\n".join(lines)
