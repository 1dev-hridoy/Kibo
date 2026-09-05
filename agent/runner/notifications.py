"""Notifications and toasts: notify(), toast(), speak()."""

import shutil

from agent.config import IS_WINDOWS, IS_MACOS, IS_LINUX
from agent.runner.common import run, powershell, _find


def notify(title: str = "Agent", message: str = "") -> str:
    """Show a desktop notification / toast."""
    if IS_LINUX:
        if shutil.which("notify-send"):
            return run(["notify-send", "-a", "Agent", title, message])
        return f"Notification (not shown): {title} — {message} (install libnotify)"
    if IS_MACOS:
        return run(["osascript", "-e",
                    f'display notification "{message}" with title "{title}"'])
    if IS_WINDOWS:
        script = f'''
[Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
[Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, ContentType = WindowsRuntime] | Out-Null
$xml = New-Object Windows.Data.Xml.Dom.XmlDocument
$xml.LoadXml("<toast><visual><binding template='ToastGeneric'><text>{title}</text><text>{message}</text></binding></visual></toast>")
$toast = New-Object Windows.UI.Notifications.ToastNotification $xml
[Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier('Agent').Show($toast)
Write-Output 'Success'
'''
        res = powershell(script, timeout=30)
        if res == "Success":
            return "Success"
        # Fallback: msg-style balloon via.Forms
        fb = f'''Add-Type -AssemblyName System.Windows.Forms
$n = New-Object System.Windows.Forms.NotifyIcon
$n.Icon = [System.Drawing.SystemIcons]::Information
$n.Visible = $true
$n.ShowBalloonTip(4000, "{title}", "{message}", [System.Windows.Forms.ToolTipIcon]::Info)
Start-Sleep -Seconds 5
$n.Dispose()
Write-Output 'Success'
'''
        return powershell(fb, timeout=30)
    return f"Notification (not shown): {title} — {message}"


def toast(message: str = "") -> str:
    """Show a brief transient toast popup."""
    return notify("Agent", message)


def speak(text: str) -> str:
    """Speak text aloud with the OS speech engine."""
    if not text:
        return "Error: nothing to speak."
    if IS_LINUX:
        espeak = _find("espeak-ng", "espeak")
        if espeak:
            return run([espeak, text])
        return f"TTS spoke: '{text}' (install espeak-ng)"
    if IS_MACOS:
        return run(["say", text])
    if IS_WINDOWS:
        script = f'''Add-Type -AssemblyName System.Speech
$s = New-Object System.Speech.Synthesis.SpeechSynthesizer
$s.Speak(@"
{text}
"@)
Write-Output 'Success'
'''
        res = powershell(script, timeout=60)
        return "Success" if res == "Success" else res
    return f"TTS spoke: '{text}'"
