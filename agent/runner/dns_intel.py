"""
DNS and domain intelligence — DNS lookups (Cloudflare DoH), WHOIS/RDAP
queries, IP geolocation, and subdomain takeover checks.
"""

import json
import re
import urllib.parse
import urllib.request


# ═══════════════════════════════════════════════════════════════════════
# DNS Lookup (Cloudflare DoH)
# ═══════════════════════════════════════════════════════════════════════

_VALID_DNS_TYPES = {"A", "AAAA", "MX", "TXT", "CNAME", "NS", "SRV", "SOA"}


def dns_lookup(domain: str, record_type: str = "A") -> dict:
    """Perform DNS lookup using Cloudflare DNS-over-HTTPS.

    Args:
        domain: Target domain.
        record_type: DNS record type (A, AAAA, MX, TXT, CNAME, NS).

    Returns dict with 'domain', 'records', 'resolver'.
    """
    record_type = record_type.upper()
    if record_type not in _VALID_DNS_TYPES:
        record_type = "A"

    try:
        url = f"https://cloudflare-dns.com/dns-query?name={domain}&type={record_type}"
        req = urllib.request.Request(url, headers={
            "User-Agent": "Kibo/1.0",
            "Accept": "application/dns-json",
        })
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())

        records = [
            {"type": a.get("type", ""), "name": a.get("name", ""),
             "data": a.get("data", ""), "ttl": a.get("TTL", 0)}
            for a in data.get("Answer", [])
        ]

        return {
            "domain": domain,
            "record_type": record_type,
            "records": records,
            "resolver": "Cloudflare DNS-over-HTTPS",
        }

    except Exception as e:
        return {"domain": domain, "record_type": record_type, "error": str(e)}


# ═══════════════════════════════════════════════════════════════════════
# WHOIS / RDAP Lookup
# ═══════════════════════════════════════════════════════════════════════

def whois_lookup(domain: str) -> dict:
    """Query domain registration info via RDAP API.

    Returns dict with 'domain', 'registrar', 'creation_date', 'expiry_date'.
    """
    domain = re.sub(r"^https?://", "", domain)
    domain = domain.split("/")[0].split(":")[0]

    try:
        req = urllib.request.Request(
            "https://rdap.org/domain/" + domain,
            headers={"User-Agent": "Kibo/1.0",
                      "Accept": "application/rdap+json"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())

        result = {
            "domain": domain,
            "name": data.get("ldhName", domain),
            "status": data.get("status", []),
        }

        for event in data.get("events", []):
            action = event.get("eventAction", "")
            date = event.get("eventDate", "")
            if action == "registration":
                result["creation_date"] = date
            elif action == "expiration":
                result["expiry_date"] = date
            elif action == "last changed":
                result["updated_date"] = date

        for entity in data.get("entities", []):
            if "registrar" in entity.get("roles", []):
                vcard = entity.get("vcardArray", [None, []])
                if len(vcard) > 1:
                    for item in vcard[1]:
                        if item[0] == "fn":
                            result["registrar"] = item[3]
                            break

        return result

    except Exception as e:
        return {"domain": domain, "error": str(e)}


# ═══════════════════════════════════════════════════════════════════════
# IP Geolocation
# ═══════════════════════════════════════════════════════════════════════

def ip_geolocation_lookup(ip: str) -> dict:
    """Lookup geographic location and ISP for an IP address via ip-api.com.

    Returns dict with 'ip', 'country', 'city', 'isp', 'lat', 'lon', etc.
    """
    try:
        fields = "query,status,country,regionName,city,lat,lon,isp,org,as,timezone,mobile,proxy,hosting"
        url = f"http://ip-api.com/json/{ip}?fields={fields}"
        req = urllib.request.Request(url, headers={"User-Agent": "Kibo/1.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())

        if data.get("status") == "success":
            return {
                "ip": data.get("query", ip),
                "country": data.get("country", ""),
                "region": data.get("regionName", ""),
                "city": data.get("city", ""),
                "lat": data.get("lat", 0),
                "lon": data.get("lon", 0),
                "isp": data.get("isp", ""),
                "org": data.get("org", ""),
                "as": data.get("as", ""),
                "timezone": data.get("timezone", ""),
                "mobile": data.get("mobile", False),
                "proxy": data.get("proxy", False),
                "hosting": data.get("hosting", False),
            }
        return {"ip": ip, "error": data.get("message", "Lookup failed")}

    except Exception as e:
        return {"ip": ip, "error": str(e)}


# ═══════════════════════════════════════════════════════════════════════
# Subdomain Takeover Check
# ═══════════════════════════════════════════════════════════════════════

_VULN_CNAME_PATTERNS = [
    ("s3.amazonaws.com", "AWS S3"),
    ("amazonaws.com", "AWS"),
    ("azurewebsites.net", "Azure Websites"),
    ("cloudapp.net", "Azure CloudApp"),
    ("blob.core.windows.net", "Azure Blob"),
    ("trafficmanager.net", "Azure Traffic Manager"),
    ("herokuapp.com", "Heroku"),
    ("herokudns.com", "Heroku DNS"),
    ("github.io", "GitHub Pages"),
    ("gitbook.io", "GitBook"),
    ("surge.sh", "Surge.sh"),
    ("bitbucket.io", "Bitbucket"),
    ("zendesk.com", "Zendesk"),
    ("readme.io", "ReadMe"),
    ("ghost.io", "Ghost"),
    ("shopify.com", "Shopify"),
    ("bigcartel.com", "BigCartel"),
    ("helpjuice.com", "HelpJuice"),
    ("helpscout.com", "HelpScout"),
    ("statuspage.io", "StatusPage"),
    ("pingdom.com", "Pingdom"),
    ("tave.com", "Tave"),
    ("helpshift.com", "Helpshift"),
    ("landingi.com", "Landingi"),
    ("launchrock.com", "LaunchRock"),
    ("domains.google.com", "Google Domains"),
    ("pantheon.io", "Pantheon"),
    ("ghost.org", "Ghost"),
]

_COMMON_SUBS = [
    "www", "mail", "ftp", "smtp", "pop", "imap", "webmail",
    "api", "dev", "staging", "test", "beta", "demo", "app",
    "blog", "shop", "store", "cdn", "media", "static",
    "admin", "portal", "vpn", "git", "ci", "jenkins",
    "status", "docs", "help", "support", "ns1", "ns2",
]


def check_subdomain_takeover(domain: str) -> dict:
    """Audit domain CNAME records for vulnerable dangling cloud pointers.

    Returns dict with 'domain', 'subdomains' checked, 'vulnerable', 'safe'.
    """
    results = {"domain": domain, "subdomains": [], "vulnerable": [], "safe": []}

    for sub in _COMMON_SUBS:
        fqdn = f"{sub}.{domain}"
        try:
            cname_resp = dns_lookup(fqdn, "CNAME")
            cname_records = cname_resp.get("records", [])
            a_resp = dns_lookup(fqdn, "A")
            a_records = a_resp.get("records", [])

            entry = {
                "subdomain": fqdn,
                "cname": cname_records[0]["data"] if cname_records else "",
                "a_record": a_records[0]["data"] if a_records else "",
            }

            if entry["cname"]:
                cname_lower = entry["cname"].lower()
                for pattern, provider in _VULN_CNAME_PATTERNS:
                    if pattern in cname_lower:
                        entry["vulnerable"] = True
                        entry["provider"] = provider
                        results["vulnerable"].append(entry)
                        break
                else:
                    results["safe"].append(entry)
            else:
                results["safe"].append(entry)

        except Exception:
            pass

    return results
