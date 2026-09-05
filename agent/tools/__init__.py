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
    check_internet,
)
from agent.tools.apps import open_app, open_local_path, list_files, list_installed_apps
from agent.tools.sysadmin import (
    get_running_processes, kill_a_process,
    create_file, delete_file, move_file, read_file,
    get_disk_usage, get_temperature,
    view_system_logs,
    install_package, uninstall_package,
)
from agent.tools.advanced import (
    # Remote Terminal (2)
    remote_terminal, remote_terminal_background,
    # Application Launcher (3)
    launch_app_smart, get_recent_apps, search_apps,
    # Clipboard Sync (4)
    clipboard_sync_push, clipboard_sync_pull, clipboard_sync_list, clipboard_sync_clear,
    # Media Streamer (4)
    play_media, stop_media, get_media_status, set_media_volume,
    # Voice Gateway (4)
    voice_record_start, voice_record_stop, voice_speak, voice_list_devices,
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
    # Network (5)
    get_wifi_info, scan_wifi_networks, check_internet,
    download_file, get_system_info,
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
    # ── Advanced Tools (17) ──
    # Remote Terminal (2)
    remote_terminal, remote_terminal_background,
    # Application Launcher (3)
    launch_app_smart, get_recent_apps, search_apps,
    # Clipboard Sync (4)
    clipboard_sync_push, clipboard_sync_pull, clipboard_sync_list, clipboard_sync_clear,
    # Media Streamer (4)
    play_media, stop_media, get_media_status, set_media_volume,
    # Voice Gateway (4)
    voice_record_start, voice_record_stop, voice_speak, voice_list_devices,
]
