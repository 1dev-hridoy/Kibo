"""
Core agent orchestration — wraps the Needle engine with:
  • a system prompt that teaches the tool-calling protocol
  • deterministic fast-paths for common PC commands
  • context memory for conversation history
  • envelope → text extraction
"""

from .ask import ask
from .context import (
    get_context_string, get_last_topic, get_current_task,
    clear_context, save_context
)

__all__ = ["ask", "get_context_string", "get_last_topic", "get_current_task",
           "clear_context", "save_context"]
