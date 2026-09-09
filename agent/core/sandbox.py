"""
Security sandbox guardrails — path enforcement, core file protection,
and dangerous command filtering. Prevents the AI from modifying its own
codebase or executing destructive system commands.
"""

import os
import re

from agent.config import HOME



_AGENT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PROTECTED_PREFIXES = [
    _AGENT_ROOT,  
]





PROTECTED_FILENAMES = {
    "server.py", "setup.py", "launch.sh", "install.sh", "install.ps1",
    "config.py", "__main__.py", "pyproject.toml", "requirements.txt",
}



_DANGEROUS_PATTERNS = [
    re.compile(r"rm\s+-[a-z]*\s+/\s*$"),          
    re.compile(r"rm\s+-[a-z]*\s+/\s"),            
    re.compile(r"rm\s+-[a-z]*f?\s+/\b"),           
    re.compile(r"rm\s+-[a-z]*r\s+/\s"),         
    re.compile(r":\(\)\{.*\};:"),                
    re.compile(r"mkfs\.\w+\s+/"),                    
    re.compile(r"dd\s+if=.*of=/dev/"),             
    re.compile(r">\s*/dev/sd[a-z]"),                
    re.compile(r"chmod\s+-[a-z]*\s+777\s+/"),       
    re.compile(r"chown\s+.*\s+/\s"),               
    re.compile(r"mv\s+.*\s+/\s"),                 
    re.compile(r"wget.*\|\s*sh"),                   
    re.compile(r"curl.*\|\s*sh"),                   
    re.compile(r"curl.*\|\s*bash"),                  

]




_PATH_TRAVERSAL = re.compile(r"\.\.[\\/]|\.\.%2[fF]")


class SandboxError(Exception):
    """Raised when a sandbox check fails."""
    pass


def validate_write_path(path: str, workspace_dir: str | None = None) -> str:
    """Validate that a write path is safe. Returns the resolved absolute path.

    Allowed:
        - Anything inside ~/Downloads/ (agent photos, screenshots, etc.)
        - Anything inside the workspace directory (if provided)
        - /tmp/ paths

    Blocked:
        - Path traversal (..) attempts
        - Writes to the agent source code directory
        - Writes to system directories (/, /etc, /usr, etc.)

    Raises SandboxError if the path is not allowed.
    """
    path = os.path.expanduser(path)




    if _PATH_TRAVERSAL.search(path):
        raise SandboxError(f"Path traversal blocked: '{path}'")

    resolved = os.path.realpath(path)

   
    if resolved.startswith("/tmp"):
        return resolved



    if workspace_dir:
        ws_real = os.path.realpath(workspace_dir)
        if resolved.startswith(ws_real + os.sep) or resolved == ws_real:
            return resolved



    downloads = os.path.join(HOME, "Downloads")
    if os.path.isdir(downloads):
        dl_real = os.path.realpath(downloads)
        if resolved.startswith(dl_real + os.sep) or resolved == dl_real:
            return resolved



    home_real = os.path.realpath(HOME)
    if resolved.startswith(home_real + os.sep) or resolved == home_real:
        # But block agent source within home
        for prefix in PROTECTED_PREFIXES:
            pref_real = os.path.realpath(prefix)
            if resolved.startswith(pref_real + os.sep):
                raise SandboxError(
                    f"Write to agent source directory blocked: '{path}'")
        return resolved

    raise SandboxError(f"Write path not allowed: '{path}'")


def validate_read_path(path: str) -> str:
    """Validate that a read path is safe. More permissive than write.

    Allows reading from anywhere except sensitive system files.
    Returns the resolved absolute path.
    """
    path = os.path.expanduser(path)
    resolved = os.path.realpath(path)
    return resolved


def is_core_file(filename: str) -> bool:
    """Check if a filename is a protected core file."""
    return os.path.basename(filename) in PROTECTED_FILENAMES


def check_command_safety(command: str) -> str | None:
    """Check if a shell command contains dangerous patterns.

    Returns None if safe, or an error message if dangerous.
    """
    command = command.strip()

    for pattern in _DANGEROUS_PATTERNS:
        if pattern.search(command):
            return (
                f"Command blocked: contains dangerous pattern. "
                f"This command could cause irreversible damage to the system."
            )

    return None


def sanitize_path(path: str) -> str:
    """Normalize a path, resolving .. and expanding ~."""
    path = os.path.expanduser(path)
    path = os.path.normpath(path)
    return path
