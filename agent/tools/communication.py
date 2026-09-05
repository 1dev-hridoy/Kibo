"""
Text tools — copy content to the clipboard for use in other apps
(the desktop equivalent of 'sharing').
"""

import needle
from agent.runner import clipboard_set, clipboard_get


@needle.tool
def copy_text_to_clipboard(text: str):
    """Copy text to the system clipboard so it can be pasted anywhere."""
    print(f"[Tool] copy_text_to_clipboard('{text[:30]}')")
    return clipboard_set(text)


@needle.tool
def read_clipboard_text():
    """Read the current text content of the system clipboard."""
    print("[Tool] read_clipboard_text()")
    return clipboard_get()
