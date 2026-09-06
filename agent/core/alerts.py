"""
Proactive alerts — monitor system thresholds and notify.
"""

import os
import json
import time
import threading

ALERTS_FILE = os.path.expanduser("~/.kibo_alerts.json")
_alerts = []
_alerts_lock = threading.Lock()


def _load_alerts():
    """Load alerts from disk."""
    global _alerts
    if os.path.exists(ALERTS_FILE):
        with open(ALERTS_FILE) as f:
            _alerts = json.load(f)


def _save_alerts():
    """Save alerts to disk."""
    with open(ALERTS_FILE, "w") as f:
        json.dump(_alerts, f, indent=2)


def add_alert(metric, threshold, direction, label=""):
    """Add a threshold alert.
    
    Args:
        metric: What to monitor (temperature, disk, battery, cpu, memory)
        threshold: Trigger value (e.g. 80 for 80%)
        direction: 'above' or 'below'
        label: Optional label for the alert
    """
    with _alerts_lock:
        _load_alerts()
        alert = {
            "id": len(_alerts) + 1,
            "metric": metric,
            "threshold": threshold,
            "direction": direction,
            "label": label or f"{metric} {direction} {threshold}",
            "active": True,
            "created": time.time(),
            "last_triggered": None,
            "trigger_count": 0,
        }
        _alerts.append(alert)
        _save_alerts()
        return f"Alert #{alert['id']} created: {alert['label']}"


def remove_alert(alert_id):
    """Remove an alert by ID."""
    with _alerts_lock:
        _load_alerts()
        for i, a in enumerate(_alerts):
            if a["id"] == alert_id:
                _alerts.pop(i)
                _save_alerts()
                return f"Alert #{alert_id} removed"
        return f"Alert #{alert_id} not found"


def list_alerts():
    """List all active alerts."""
    _load_alerts()
    if not _alerts:
        return "No alerts configured"
    
    result = "Configured alerts:\n"
    for a in _alerts:
        status = "ACTIVE" if a["active"] else "PAUSED"
        result += f"  #{a['id']} [{status}] {a['label']} "
        result += f"(triggered {a['trigger_count']}x)\n"
    return result


def pause_alert(alert_id):
    """Pause an alert."""
    with _alerts_lock:
        _load_alerts()
        for a in _alerts:
            if a["id"] == alert_id:
                a["active"] = False
                _save_alerts()
                return f"Alert #{alert_id} paused"
        return f"Alert #{alert_id} not found"


def resume_alert(alert_id):
    """Resume a paused alert."""
    with _alerts_lock:
        _load_alerts()
        for a in _alerts:
            if a["id"] == alert_id:
                a["active"] = True
                _save_alerts()
                return f"Alert #{alert_id} resumed"
        return f"Alert #{alert_id} not found"


def _get_metric_value(metric):
    """Get current value for a metric."""
    try:
        if metric == "temperature":
            from agent.runner.sysadmin import get_temperature
            result = get_temperature()


            
            import re
            m = re.search(r"(\d+(?:\.\d+)?)", result)
            return float(m.group(1)) if m else None

        elif metric == "disk":
            from agent.runner.sysadmin import get_disk_usage
            result = get_disk_usage()
            import re
            m = re.search(r"(\d+(?:\.\d+)?)%", result)
            return float(m.group(1)) if m else None

        elif metric == "battery":
            from agent.tools.system import get_battery_status
            result = get_battery_status()
            import re
            m = re.search(r"(\d+)%", result)
            return float(m.group(1)) if m else None

        elif metric == "cpu":
            import psutil
            return psutil.cpu_percent(interval=1)

        elif metric == "memory":
            import psutil
            return psutil.virtual_memory().percent

    except Exception:
        return None


def check_alerts():
    """Check all alerts and return triggered ones."""
    _load_alerts()
    triggered = []

    for alert in _alerts:
        if not alert["active"]:
            continue

        value = _get_metric_value(alert["metric"])
        if value is None:
            continue

        should_trigger = False
        if alert["direction"] == "above" and value > alert["threshold"]:
            should_trigger = True
        elif alert["direction"] == "below" and value < alert["threshold"]:
            should_trigger = True

        if should_trigger:
            alert["last_triggered"] = time.time()
            alert["trigger_count"] += 1
            triggered.append({
                "id": alert["id"],
                "label": alert["label"],
                "metric": alert["metric"],
                "value": value,
                "threshold": alert["threshold"],
                "direction": alert["direction"],
            })

    if triggered:
        with _alerts_lock:
            _save_alerts()

    return triggered


def format_alert(trigger):
    """Format a triggered alert for display."""
    return (
        f"⚠️ Alert #{trigger['id']}: {trigger['label']}\n"
        f"   {trigger['metric']} = {trigger['value']:.1f} "
        f"({trigger['direction']} {trigger['threshold']})"
    )
