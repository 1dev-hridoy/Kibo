"""Agent runner subpackage — cross-platform native capability layer."""

# common
from agent.runner.common import (
    CREATE_NO_WINDOW,
    _find,
    _pkg_hint,
    run,
    run_cmd,
    run_cmd_json,
    powershell,
    StatefulShell,
    get_persistent_shell,
    run_persistent,
)

# notifications
from agent.runner.notifications import notify, toast, speak

# display
from agent.runner.display import set_brightness

# battery
from agent.runner.battery import has_battery, battery_status

# clipboard
from agent.runner.clipboard import clipboard_set, clipboard_get

# audio
from agent.runner.audio import (
    volume_info,
    set_volume,
    _RECORD_STATE,
    record_audio_start,
    record_audio_stop,
)

# wifi
from agent.runner.wifi import _local_ip, wifi_info, wifi_scan

# system_info
from agent.runner.system_info import (
    system_info,
    device_info,
    has_internet,
    system_stats,
)

# apps
from agent.runner.apps import (
    _startfile,
    launch,
    open_url,
    open_path,
    copy_to_clipboard,
    download_file,
)

# media
from agent.runner.media import camera_photo

# screen
from agent.runner.screen import take_screenshot, lock_screen

# power
from agent.runner.power import power_action

# files
from agent.runner.files import (
    list_files,
    list_installed_apps,
    file_create,
    file_delete,
    file_move,
    file_read,
)

# processes
from agent.runner.processes import list_processes, kill_process

# disk
from agent.runner.disk import disk_usage, system_temperature

# logs_viewer
from agent.runner.logs_viewer import view_logs

# packages
from agent.runner.packages import package_install, package_uninstall

# web
from agent.runner.web import web_search_and_extract, fetch_url_text

# network scan
from agent.runner.network_scan import (
    local_network_scan,
    subnet_port_sweep,
    local_port_scan,
    list_local_listeners,
)

# security audit
from agent.runner.security_audit import (
    detect_arp_spoofing,
    audit_vpn_connection,
    audit_website_security,
)

# dns intel
from agent.runner.dns_intel import (
    dns_lookup,
    whois_lookup,
    ip_geolocation_lookup,
    check_subdomain_takeover,
)

# hashing
from agent.runner.hashing import generate_checksum, hash_string, identify_hash

# jwt
from agent.runner.jwt_analyzer import decode_jwt

# forensics
from agent.runner.forensics import analyze_pcap, analyze_apk, search_file_content

__all__ = [
    # common
    "CREATE_NO_WINDOW",
    "_find",
    "_pkg_hint",
    "run",
    "run_cmd",
    "run_cmd_json",
    "powershell",
    "StatefulShell",
    "get_persistent_shell",
    "run_persistent",
    # notifications
    "notify",
    "toast",
    "speak",
    # display
    "set_brightness",
    # battery
    "has_battery",
    "battery_status",
    # clipboard
    "clipboard_set",
    "clipboard_get",
    # audio
    "volume_info",
    "set_volume",
    "_RECORD_STATE",
    "record_audio_start",
    "record_audio_stop",
    # wifi
    "_local_ip",
    "wifi_info",
    "wifi_scan",
    # system_info
    "system_info",
    "device_info",
    "has_internet",
    "system_stats",
    # apps
    "_startfile",
    "launch",
    "open_url",
    "open_path",
    "copy_to_clipboard",
    "download_file",
    # media
    "camera_photo",
    # screen
    "take_screenshot",
    "lock_screen",
    # power
    "power_action",
    # files
    "list_files",
    "list_installed_apps",
    "file_create",
    "file_delete",
    "file_move",
    "file_read",
    # processes
    "list_processes",
    "kill_process",
    # disk
    "disk_usage",
    "system_temperature",
    # logs_viewer
    "view_logs",
    # packages
    "package_install",
    "package_uninstall",
    # web
    "web_search_and_extract",
    "fetch_url_text",
    # network scan
    "local_network_scan",
    "subnet_port_sweep",
    "local_port_scan",
    "list_local_listeners",
    # security audit
    "detect_arp_spoofing",
    "audit_vpn_connection",
    "audit_website_security",
    # dns intel
    "dns_lookup",
    "whois_lookup",
    "ip_geolocation_lookup",
    "check_subdomain_takeover",
    # hashing
    "generate_checksum",
    "hash_string",
    "identify_hash",
    # jwt
    "decode_jwt",
    # forensics
    "analyze_pcap",
    "analyze_apk",
    "search_file_content",
]
