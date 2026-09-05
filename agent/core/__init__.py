"""
Core agent orchestration — wraps the Needle engine with:
  • a system prompt that teaches the tool-calling protocol
  • deterministic fast-paths for common PC commands
  • envelope → text extraction
"""

from .ask import ask

__all__ = ["ask"]
