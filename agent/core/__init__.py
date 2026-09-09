"""
Core agent orchestration — wraps the Needle engine with:
  • a system prompt that teaches the tool-calling protocol
  • deterministic fast-paths for common PC commands
  • context memory for conversation history
  • envelope → text extraction
  • security sandbox guardrails
"""

from .ask import ask
from .context import (
    get_context_string, get_last_topic, get_current_task,
    clear_context, save_context
)


from .sandbox import validate_write_path, validate_read_path, check_command_safety, SandboxError



__all__ = ["ask", "get_context_string", "get_last_topic", "get_current_task",
           "clear_context", "save_context",
           "validate_write_path", "validate_read_path", "check_command_safety",
           "SandboxError"]
