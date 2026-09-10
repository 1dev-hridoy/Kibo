"""
Forensic analysis — PCAP packet capture parsing, APK manifest analysis,
and recursive file content search.
"""

import glob
import os
import re
import subprocess
import zipfile


# ═══════════════════════════════════════════════════════════════════════
# PCAP Analyzer
# ═══════════════════════════════════════════════════════════════════════

def analyze_pcap(file_path: str) -> dict:
    """Parse a pcap file using tcpdump and extract HTTP, DNS, and login data.

    Args:
        file_path: Path to the .pcap or .pcapng file.

    Returns dict with summary stats and extracted info.
    """
    if not os.path.isfile(file_path):
        return {"error": f"File not found: {file_path}"}

    result = {"file": file_path, "stats": {}, "http": [], "dns": [], "logins": []}



  
    try:
        r = subprocess.run(
            ["tcpdump", "-r", file_path, "-nn", "-q"],
            capture_output=True, text=True, timeout=30, errors="replace")
        lines = r.stdout.strip().splitlines()
        result["stats"]["total_packets"] = len(lines)



     
        protocols = {}
        for line in lines:
            parts = line.split()
            if len(parts) > 2:
                proto = parts[2].rstrip(":")
                protocols[proto] = protocols.get(proto, 0) + 1
        result["stats"]["protocols"] = dict(sorted(protocols.items(), key=lambda x: -x[1])[:10])
    except FileNotFoundError:
        return {"error": "tcpdump not found — install with: sudo apt install tcpdump"}
    except Exception as e:
        return {"error": f"tcpdump error: {e}"}




    try:
        r = subprocess.run(
            ["tcpdump", "-r", file_path, "-A", "-s", "0", "port", "80", "port", "443"],
            capture_output=True, text=True, timeout=60, errors="replace")
        for line in r.stdout.splitlines():
            if "HTTP/" in line:
                match = re.search(r"(GET|POST|PUT|DELETE|PATCH)\s+(\S+)", line)
                if match:
                    result["http"].append({"method": match.group(1), "url": match.group(2)})
            if re.search(r"(password|passwd|pwd|secret|token|key)\s*[:=]", line, re.I):
                result["logins"].append(line.strip()[:200])
    except Exception:
        pass




    try:
        r = subprocess.run(
            ["tcpdump", "-r", file_path, "-nn", "port", "53"],
            capture_output=True, text=True, timeout=30, errors="replace")
        seen = set()
        for line in r.stdout.splitlines():
            if "A?" in line or "AAAA?" in line:
                parts = line.split()
                for i, p in enumerate(parts):
                    if p in ("A?", "AAAA?") and i > 0:
                        domain = parts[i - 1].rstrip(".")
                        if domain not in seen:
                            seen.add(domain)
                            result["dns"].append({"domain": domain})
                            if len(result["dns"]) >= 50:
                                break
    except Exception:
        pass

    return result





# ═══════════════════════════════════════════════════════════════════════
# APK Manifest Analyzer
# ═══════════════════════════════════════════════════════════════════════

_DANGEROUS_PERMS = {
    "android.permission.READ_SMS": "Read SMS",
    "android.permission.RECEIVE_SMS": "Receive SMS",
    "android.permission.SEND_SMS": "Send SMS",
    "android.permission.READ_CONTACTS": "Read contacts",
    "android.permission.WRITE_CONTACTS": "Modify contacts",
    "android.permission.READ_CALL_LOG": "Read call history",
    "android.permission.WRITE_CALL_LOG": "Modify call history",
    "android.permission.CAMERA": "Camera access",
    "android.permission.RECORD_AUDIO": "Microphone access",
    "android.permission.READ_PHONE_STATE": "Phone state (IMEI)",
    "android.permission.READ_PHONE_NUMBERS": "Phone number",
    "android.permission.ACCESS_FINE_LOCATION": "Precise GPS",
    "android.permission.ACCESS_COARSE_LOCATION": "Approximate location",
    "android.permission.ACCESS_BACKGROUND_LOCATION": "Background location",
    "android.permission.READ_EXTERNAL_STORAGE": "Read storage",
    "android.permission.WRITE_EXTERNAL_STORAGE": "Write storage",
    "android.permission.READ_MEDIA_IMAGES": "Read images",
    "android.permission.READ_MEDIA_VIDEO": "Read videos",
    "android.permission.READ_MEDIA_AUDIO": "Read audio files",
    "android.permission.READ_CALENDAR": "Read calendar",
    "android.permission.WRITE_CALENDAR": "Modify calendar",
    "android.permission.PROCESS_OUTGOING_CALLS": "Intercept calls",
    "android.permission.BODY_SENSORS": "Body sensors (heart rate)",
    "android.permission.READ_MEDIA_VISUAL_USER_SELECTED": "User-selected media",
    "android.permission.NEARBY_WIFI_DEVICES": "Nearby WiFi devices",
    "android.permission.BLUETOTH_SCAN": "Bluetooth scanning",
}

_DANGEROUS_FLAGS = [
    ("android:debuggable", "Application is debuggable"),
    ("android:allowBackup", "Application backup allowed"),
    ("android:networkSecurityConfig", "Custom network security config"),
    ("android:usesCleartextTraffic", "Allows cleartext HTTP traffic"),
]




def analyze_apk(file_path: str) -> dict:
    """Analyze an APK file's AndroidManifest.xml for permissions and flags.

    Args:
        file_path: Path to the .apk file.

    Returns dict with permissions, dangerous permissions, and security flags.
    """
    if not os.path.isfile(file_path):
        return {"error": f"File not found: {file_path}"}

    if not file_path.endswith(".apk"):
        return {"error": "File does not have .apk extension"}

    try:
        with zipfile.ZipFile(file_path, "r") as zf:
            if "AndroidManifest.xml" not in zf.namelist():
                return {"error": "No AndroidManifest.xml found in APK"}

            manifest_raw = zf.read("AndroidManifest.xml")

    except zipfile.BadZipFile:
        return {"error": "Invalid APK/ZIP file"}
    except Exception as e:
        return {"error": str(e)}




    
    result = _analyze_apk_aapt(file_path)
    if not result.get("error"):
        return result




  
    return _analyze_apk_binary(manifest_raw, file_path)


def _analyze_apk_aapt(file_path: str) -> dict:
    """Use aapt to parse the APK manifest."""
    try:
        r = subprocess.run(
            ["aapt", "dump", "permissions", file_path],
            capture_output=True, text=True, timeout=30, errors="replace")
        if r.returncode != 0:
            return {"error": "aapt not available"}

        all_perms = []
        for line in r.stdout.splitlines():
            match = re.search(r"uses-permission:\s*name='([^']+)'", line)
            if match:
                all_perms.append(match.group(1))






        r2 = subprocess.run(
            ["aapt", "dump", "badging", file_path],
            capture_output=True, text=True, timeout=30, errors="replace")

        package = version = min_sdk = target_sdk = ""
        flags = {}
        for line in r2.stdout.splitlines():
            if line.startswith("package:"):
                for part in line.split():
                    if "name=" in part:
                        package = part.split("=")[1].strip("'\"")
                    if "versionName=" in part:
                        version = part.split("=")[1].strip("'\"")
            if "sdkVersion:" in line:
                min_sdk = line.split("'")[1] if "'" in line else line.split(":")[-1].strip()
            if "targetSdkVersion:" in line:
                target_sdk = line.split("'")[1] if "'" in line else line.split(":")[-1].strip()

        return _format_apk_result(
            package, version, min_sdk, target_sdk, all_perms, {}, file_path)

    except FileNotFoundError:
        return {"error": "aapt not found — install android-sdk-build-tools"}
    except Exception as e:
        return {"error": str(e)}



    


def _analyze_apk_binary(data: bytes, file_path: str) -> dict:
    """Extract strings from binary AndroidManifest.xml."""
    try:
        text = data.decode("utf-8", errors="ignore")
        perm_pattern = re.compile(r"android\.permission\.[A-Z_]+")
        matches = perm_pattern.findall(text)
        all_perms = list(set(matches))

        flags = {}
        for flag_key, desc in _DANGEROUS_FLAGS:
            if flag_key.encode() in data:
                flags[flag_key] = desc

        return _format_apk_result(
            "", "", "", "", all_perms, flags, file_path)

    except Exception as e:
        return {"error": f"Failed to parse manifest: {e}"}







def _format_apk_result(package, version, min_sdk, target_sdk,
                       all_perms, extra_flags, file_path) -> dict:
    """Format APK analysis result."""
    dangerous = []
    for perm in all_perms:
        if perm in _DANGEROUS_PERMS:
            dangerous.append({"permission": perm, "description": _DANGEROUS_PERMS[perm]})

    sec_flags = {}
    for flag_key, desc in _DANGEROUS_FLAGS:
        if flag_key in extra_flags:
            sec_flags[flag_key] = extra_flags[flag_key]



    return {

        "package": package,
        "version": version,
        "min_sdk": min_sdk,
        "target_sdk": target_sdk,
        "total_permissions": len(all_perms),
        "dangerous_permissions": dangerous,
        "all_permissions": all_perms[:50],
        "security_flags": sec_flags,
        "file": file_path,
        "size_bytes": os.path.getsize(file_path),
    }





# ═══════════════════════════════════════════════════════════════════════
# File Content Search (recursive grep)
# ═══════════════════════════════════════════════════════════════════════

def search_file_content(directory: str, pattern: str,
                        glob_filter: str = "*",
                        max_results: int = 200) -> dict:
    """Search file contents recursively in a directory.

    Args:
        directory: Root directory to search.
        pattern: Regex pattern to search for.
        glob_filter: File pattern filter (e.g. '*.py', '*.py,*.js').
        max_results: Maximum results to return.

    Returns dict with matches grouped by file.
    """
    if not os.path.isdir(directory):
        return {"error": f"Directory not found: {directory}"}

    try:
        regex = re.compile(pattern, re.IGNORECASE)
    except re.error as e:
        return {"error": f"Invalid regex: {e}"}

    filters = [f.strip() for f in glob_filter.split(",") if f.strip()]

    results = {}
    total_matches = 0

    for filt in filters:
        for file_path in glob.glob(os.path.join(directory, "**", filt), recursive=True):
            if not os.path.isfile(file_path):
                continue
            if total_matches >= max_results:
                break
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    for line_num, line in enumerate(f, 1):
                        if regex.search(line):
                            rel = os.path.relpath(file_path, directory)
                            if rel not in results:
                                results[rel] = []
                            results[rel].append({
                                "line": line_num,
                                "text": line.rstrip()[:300],
                            })
                            total_matches += 1
                            if total_matches >= max_results:
                                break
            except (OSError, PermissionError):
                pass
        if total_matches >= max_results:
            break

    return {
        "directory": os.path.abspath(directory),
        "pattern": pattern,
        "total_matches": total_matches,
        "files": dict(list(results.items())[:50]),
    }
