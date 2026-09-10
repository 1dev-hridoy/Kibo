"""
Crypto & forensics tool wrappers — hashing, JWT, PCAP, APK, content search.
"""

import needle

from agent.runner.hashing import (
    generate_checksum as _checksum,
    hash_string as _hash_str,
    identify_hash as _identify,
)
from agent.runner.jwt_analyzer import decode_jwt as _jwt
from agent.runner.forensics import (
    analyze_pcap as _pcap,
    analyze_apk as _apk,
    search_file_content as _search,
)





@needle.tool
def generate_file_checksum(file_path: str) -> str:
    """Generate MD5, SHA1, SHA256, and SHA512 checksums for a file.
    Use for: verifying file integrity, checking downloads, malware analysis."""
    print(f"[Tool] generate_file_checksum('{file_path}')")
    result = _checksum(file_path)
    if result.get("error"):
        return f"Error: {result['error']}"
    lines = [f"File: {result['file']} ({result['size_bytes']} bytes)\n"]
    for algo, digest in result["hashes"].items():
        lines.append(f"  {algo.upper():>8}: {digest}")

    return "\n".join(lines)




@needle.tool
def hash_text(text: str, algorithm: str = "sha256") -> str:
    """Hash a plaintext string with the specified algorithm.
    Use for: generating password hashes, checksums, data fingerprinting.
    Supported: md5, sha1, sha256, sha512, sha3_256, blake2b."""
    print(f"[Tool] hash_text('{text[:20]}...', '{algorithm}')")
    result = _hash_str(text, algorithm)
    if result.get("error"):
        return f"Error: {result['error']}"
    return f"{result['algorithm'].upper()}: {result['hash']}"






@needle.tool
def identify_hash_algorithm(hash_value: str) -> str:
    """Identify what hash algorithm was used to produce a given hash.
    Use for: analyzing unknown hashes in security investigations."""
    print(f"[Tool] identify_hash_algorithm('{hash_value[:30]}...')")
    result = _identify(hash_value)
    algos = result.get("possible_algorithms", [])
    lines = [f"Hash length: {result['length']} chars"]
    lines.append(f"Pure hex: {'yes' if result['hex'] else 'no'}")
    if algos:
        lines.append(f"Possible algorithms: {', '.join(algos)}")
    else:
        lines.append("No known algorithm matched")
    return "\n".join(lines)




@needle.tool
def decode_jwt_token(token: str) -> str:
    """Decode a JWT (JSON Web Token) and audit its security.
    Use for: debugging auth tokens, checking for 'none' algorithm
    vulnerabilities, inspecting token expiry and claims."""
    print(f"[Tool] decode_jwt_token('{token[:30]}...')")
    result = _jwt(token)
    if result.get("error"):
        return f"Error: {result['error']}"

    lines = ["JWT Header:"]
    for k, v in result["header"].items():
        lines.append(f"  {k}: {v}")

    lines.append("\nJWT Payload:")
    for k, v in result["payload"].items():
        lines.append(f"  {k}: {v}")

    lines.append(f"\nSignature: {result['signature']}")

    warnings = result.get("warnings", [])
    if warnings:
        lines.append("\n⚠ Security Warnings:")
        for w in warnings:
            lines.append(f"  {w}")

    return "\n".join(lines)




@needle.tool
def analyze_pcap_file(file_path: str) -> str:
    """Analyze a network packet capture (pcap) file.
    Extracts HTTP requests, DNS queries, and potential login credentials.
    Use for: network forensics, incident response, traffic analysis."""
    print(f"[Tool] analyze_pcap_file('{file_path}')")
    result = _pcap(file_path)
    if result.get("error"):
        return f"Error: {result['error']}"



    stats = result.get("stats", {})
    lines = [f"Pcap: {result['file']}"]
    lines.append(f"  Packets: {stats.get('total_packets', '?')}")
    protos = stats.get("protocols", {})
    if protos:
        lines.append(f"  Top protocols: {protos}")



    http = result.get("http", [])
    if http:
        lines.append(f"\n  HTTP Requests ({len(http)}):")
        for h in http[:10]:
            lines.append(f"    {h['method']} {h['url'][:100]}")



    dns = result.get("dns", [])
    if dns:
        lines.append(f"\n  DNS Queries ({len(dns)}):")
        for d in dns[:10]:
            lines.append(f"    {d['domain']}")



    logins = result.get("logins", [])
    if logins:
        lines.append(f"\n  ⚠ Potential Credentials Found ({len(logins)}):")
        for l in logins[:5]:
            lines.append(f"    {l[:120]}")


    return "\n".join(lines)




@needle.tool
def analyze_apk_permissions(file_path: str) -> str:
    """Analyze an Android APK for permissions and security flags.
    Checks: dangerous permissions, debug mode, backup enabled,
    cleartext traffic, and network security config.
    Use for: mobile app security review."""
    print(f"[Tool] analyze_apk_permissions('{file_path}')")
    result = _apk(file_path)
    if result.get("error"):
        return f"Error: {result['error']}"

    lines = [f"APK: {result['package'] or result['file']}"]
    if result.get("version"):
        lines.append(f"  Version: {result['version']}")
    if result.get("min_sdk"):
        lines.append(f"  Min SDK: {result['min_sdk']}")
    lines.append(f"  Permissions: {result['total_permissions']} total")
    lines.append(f"  Size: {result['size_bytes'] / 1024:.1f} KB")

    dangerous = result.get("dangerous_permissions", [])
    if dangerous:
        lines.append(f"\n  ⚠ Dangerous Permissions ({len(dangerous)}):")
        for d in dangerous:
            lines.append(f"    {d['description']}: {d['permission']}")
    else:
        lines.append("\n  ✓ No dangerous permissions")

    flags = result.get("security_flags", {})
    if flags:
        lines.append("\n  Security Flags:")
        for k, v in flags.items():
            lines.append(f"    ⚠ {k}")



    all_perms = result.get("all_permissions", [])
    if all_perms and len(all_perms) > len(dangerous):
        lines.append(f"\n  All permissions ({len(all_perms)}):")
        for p in all_perms[:20]:
            lines.append(f"    {p}")
        if len(all_perms) > 20:
            lines.append(f"    ... and {len(all_perms) - 20} more")

    return "\n".join(lines)




@needle.tool
def search_content(directory: str, pattern: str,
                   file_filter: str = "*") -> str:
    """Search file contents recursively in a directory using regex.
    Use for: finding hardcoded secrets, TODOs, config values,
    or any text pattern across a codebase.
    File filter: comma-separated globs (e.g. '*.py,*.js,*.env')."""
    print(f"[Tool] search_content('{directory}', '{pattern}', '{file_filter}')")
    result = _search(directory, pattern, file_filter)
    if result.get("error"):
        return f"Error: {result['error']}"



    total = result["total_matches"]
    files = result["files"]

    lines = [f"Found {total} matches for '{pattern}' in {result['directory']}"]

    for fname, matches in list(files.items())[:20]:
        lines.append(f"\n  {fname} ({len(matches)} matches):")
        for m in matches[:5]:
            lines.append(f"    L{m['line']}: {m['text'][:120]}")
        if len(matches) > 5:
            lines.append(f"    ... and {len(matches) - 5} more in this file")

    if total >= 200:
        lines.append(f"\n  (truncated at 200 results)")

    return "\n".join(lines)
