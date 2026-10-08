"""
Model-management and system-info fast-path routing.
Split out of fastpath.py to keep modules within the line cap.
"""
import re
from datetime import datetime




def model_route(t):
    m = re.match(r"^(?:switch|change|use)\s+(?:to\s+)?(?:the\s+)?(?:model\s+)?(\w+)$", t)
    if m:
        if m.group(1).lower() in ("model", "models"):
            return "__models__", None
        return "__switch_model__", m.group(1).lower()
    if t in ("needle", "needle2", "n", "gemma", "google", "func", "functiongemma", "fg"):



        return "__switch_model__", t
    if re.match(r"^(?:what|which|current|active)\s+model$", t):


        
        return "__current_model__", None
    if re.match(r"^(?:list|show)\s+models?$", t):
        return "__models__", None

    return None


def sys_route(t):
    # ═══════════════════════════════════════════════════════════════════
    # SCREENSHOT
    # ═══════════════════════════════════════════════════════════════════
    if re.search(r"\b(screenshot|screen ?shot|capture|snip)\b", t):
        return [("take_screenshot_now", {})]
    if re.match(r"^(?:take|grab|get|capture)\s+(?:a\s+)?(?:screen|screenshot|pic|photo)$", t):
        return [("take_screenshot_now", {})]

    # ═══════════════════════════════════════════════════════════════════
    # LOCK / SHUTDOWN / RESTART / SLEEP
    # ═══════════════════════════════════════════════════════════════════
    if re.search(r"\block\b", t):
        return [("lock_screen_now", {})]
    if re.search(r"\b(shut ?down|power ?off|turn off)\b", t):
        return [("power_control", {"action": "shutdown"})]
    if re.search(r"\b(restart|reboot)\b", t):
        return [("power_control", {"action": "restart"})]
    if re.search(r"\b(sleep|suspend|hibernate)\b", t):
        return [("power_control", {"action": "sleep"})]

    # ═══════════════════════════════════════════════════════════════════
    # BATTERY
    # ═══════════════════════════════════════════════════════════════════
    if re.search(r"\b(battery|charge|charging)\b", t):
        return [("get_battery_status", {})]

    # ═══════════════════════════════════════════════════════════════════
    # SYSTEM INFO
    # ═══════════════════════════════════════════════════════════════════
    if re.search(r"\b(cpu|ram|memory)\b", t):
        return [("get_system_stats", {})]
    if re.search(r"\b(device|system|pc|computer|machine|specs?|info)\b", t):
        return [("get_device_info", {})]
    if re.search(r"\b(temperature|temp|thermal|hot|heat)\b", t):
        return [("get_temperature", {})]
    if re.search(r"\b(disk|drive|storage|space)\b", t):
        return [("get_disk_usage", {})]
    if re.search(r"\b(internet|online|connect|wifi|network)\b", t) and \
       re.search(r"\b(check|is|am i|status|working)\b", t):
        return [("check_internet", {})]

    # ═══════════════════════════════════════════════════════════════════
    # WIFI
    # ═══════════════════════════════════════════════════════════════════
    if re.search(r"\b(wi-?fi|network|ssid)\b", t):
        if re.search(r"\b(scan|nearby|around|available|list|see)\b", t):
            return [("scan_wifi_networks", {})]
        return [("get_wifi_info", {})]

    # ═══════════════════════════════════════════════════════════════════
    # TIME / DATE
    # ═══════════════════════════════════════════════════════════════════
    if re.search(r"\b(time|clock|hour)\b", t) and \
       re.search(r"\b(what|whats|tell|current|now|is it)\b", t):
        now = datetime.now().strftime("%I:%M %p")
        return "__reply__", f"The current time is {now}."
    if re.search(r"\b(date|day|today)\b", t) and \
       re.search(r"\b(what|whats|tell|current|now|is it)\b", t):
        now = datetime.now().strftime("%A, %B %d, %Y")
        return "__reply__", f"Today is {now}."

    return None
