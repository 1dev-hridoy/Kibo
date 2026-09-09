"""
Tool registry — imports all tool modules and exports a flat list of tools.
This is the single source of truth for what the agent can do.
"""

from agent.tools.system import (
    show_toast, show_notification, get_battery_status,
    set_clipboard, get_clipboard, set_screen_brightness,
    get_volume_info, set_volume, lock_the_screen, get_system_stats,
)
from agent.tools.hardware import (
    get_device_info, take_screenshot_now, lock_screen_now, power_control,
)
from agent.tools.communication import (
    copy_text_to_clipboard, read_clipboard_text,
)
from agent.tools.media import (
    take_camera_photo, text_to_speech,
    record_audio_start, record_audio_stop,
)
from agent.tools.network import (
    get_wifi_info, scan_wifi_networks, download_file, get_system_info,
    check_internet, web_search, fetch_url,
)
from agent.tools.apps import open_app, open_local_path, list_files, list_installed_apps
from agent.tools.sysadmin import (
    get_running_processes, kill_a_process,
    create_file, delete_file, move_file, read_file,
    get_disk_usage, get_temperature,
    view_system_logs,
    install_package, uninstall_package,
    check_system_health,
)
from agent.tools.advanced import (
    remote_terminal, remote_terminal_background,
    launch_app_smart, get_recent_apps, search_apps,
    clipboard_sync_push, clipboard_sync_pull, clipboard_sync_list, clipboard_sync_clear,
    play_media, stop_media, get_media_status, set_media_volume,
    voice_record_start, voice_record_stop, voice_speak, voice_list_devices,
)
from agent.runner.process_control import (
    focus_app, minimize_app, maximize_app, close_app,
    type_in_app, hotkey_in_app, list_windows, get_active_window,
)
from agent.tools.automation import (
    check_system_alerts, get_alert_summary,
    schedule_agent_task, schedule_shell_task,
)
from agent.tools.macros import (
    start_macro_recording, stop_macro_recording, replay_macro,
    list_macros, delete_macro, get_macro_status,
)
from agent.tools.multi_pc import (
    register_remote_pc, unregister_remote_pc, list_remote_pcs,
    switch_to_pc, get_current_pc, ping_remote_pc, execute_on_remote_pc,
)
from agent.tools.security import (
    local_network_scan, subnet_port_sweep, local_port_scan,
    list_local_listeners, detect_arp_spoofing, audit_vpn_connection,
    audit_website_security, dns_lookup, whois_lookup,
    ip_geolocation_lookup, check_subdomain_takeover,
)

ALL_TOOLS = [
    # System (10)
    show_toast, show_notification, get_battery_status,
    set_clipboard, get_clipboard, set_screen_brightness,
    get_volume_info, set_volume, lock_the_screen, get_system_stats,
    # Hardware & power (4)
    get_device_info, take_screenshot_now, lock_screen_now, power_control,
    # Clipboard (2)
    copy_text_to_clipboard, read_clipboard_text,
    # Media (4)
    take_camera_photo, text_to_speech,
    record_audio_start, record_audio_stop,
    # Network (7)
    get_wifi_info, scan_wifi_networks, check_internet,
    download_file, get_system_info, web_search, fetch_url,
    # Apps & Files (4)
    open_app, open_local_path, list_files, list_installed_apps,
    # Process management (2)
    get_running_processes, kill_a_process,
    # File management (4)
    create_file, delete_file, move_file, read_file,
    # Disk & temp (2)
    get_disk_usage, get_temperature,
    # Logs (1)
    view_system_logs,
    # Package management (2)
    install_package, uninstall_package,
    # System Health (1)
    check_system_health,
    # Advanced (17)
    remote_terminal, remote_terminal_background,
    launch_app_smart, get_recent_apps, search_apps,
    clipboard_sync_push, clipboard_sync_pull, clipboard_sync_list, clipboard_sync_clear,
    play_media, stop_media, get_media_status, set_media_volume,
    voice_record_start, voice_record_stop, voice_speak, voice_list_devices,
    # Process Control (8)
    focus_app, minimize_app, maximize_app, close_app,
    type_in_app, hotkey_in_app, list_windows, get_active_window,
    # Automation (4)
    check_system_alerts, get_alert_summary,
    schedule_agent_task, schedule_shell_task,
   
    start_macro_recording, stop_macro_recording, replay_macro,
    list_macros, delete_macro, get_macro_status,

  
    register_remote_pc, unregister_remote_pc, list_remote_pcs,
    switch_to_pc, get_current_pc, ping_remote_pc, execute_on_remote_pc,

    # network security
    local_network_scan, subnet_port_sweep, local_port_scan,
    list_local_listeners, detect_arp_spoofing, audit_vpn_connection,
    audit_website_security, dns_lookup, whois_lookup,
    ip_geolocation_lookup, check_subdomain_takeover,
]
