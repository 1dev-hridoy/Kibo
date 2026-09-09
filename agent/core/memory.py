"""
Self-evolving memory system — Hermes-style persistent memory that
auto-updates user profile, long-term memory, and agent directives
via background conversation reflection.

Memory files:
    user.md   — User profile, preferences, interests
    memory.md — System configurations, conventions, learned lessons
    agent.md  — Agent behavior directives, tone, custom rules
"""

import os
import threading
import time

from agent.config import HOME




MEMORY_DIR = os.path.join(HOME, ".kibo_memory")
USER_FILE = os.path.join(MEMORY_DIR, "user.md")
MEMORY_FILE = os.path.join(MEMORY_DIR, "memory.md")
AGENT_FILE = os.path.join(MEMORY_DIR, "agent.md")




DEFAULT_USER_MD = """# User Profile
<!-- Auto-updated by Kibo based on conversations -->

- Name: (not yet known)
- Preferences: (learning...)
"""

DEFAULT_MEMORY_MD = """# Long-Term Memory
<!-- Auto-updated by Kibo — stores conventions, system info, lessons learned -->

- System: (scanning...)
"""

DEFAULT_AGENT_MD = """# Agent Directives
<!-- Custom behavior rules for Kibo -->

- Be helpful, concise, and accurate.
- Always verify actions before confirming success.
- Use tools proactively when they can help.
- Maintain a friendly, professional tone.
"""




_reflect_lock = threading.Lock()
_last_reflection = 0.0

REFLECTION_COOLDOWN = 10.0


def init_memory():
    """Initialize memory directory and files if they don't exist."""
    os.makedirs(MEMORY_DIR, exist_ok=True)

    defaults = {
        USER_FILE: DEFAULT_USER_MD,
        MEMORY_FILE: DEFAULT_MEMORY_MD,
        AGENT_FILE: DEFAULT_AGENT_MD,
    }
    for path, content in defaults.items():
        if not os.path.exists(path):
            try:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(content)
            except IOError:
                pass


def load_user_profile() -> str:
    """Load the user profile markdown."""
    try:
        with open(USER_FILE, "r", encoding="utf-8") as f:
            return f.read().strip()
    except (IOError, OSError):
        return DEFAULT_USER_MD


def load_memory() -> str:
    """Load the long-term memory markdown."""
    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            return f.read().strip()
    except (IOError, OSError):
        return DEFAULT_MEMORY_MD


def load_agent_directives() -> str:
    """Load the agent behavior directives markdown."""
    try:
        with open(AGENT_FILE, "r", encoding="utf-8") as f:
            return f.read().strip()
    except (IOError, OSError):
        return DEFAULT_AGENT_MD




def get_memory_context() -> str:
    """Get all memory files as a single context string for prompt injection."""
    init_memory()

    user = load_user_profile()
    memory = load_memory()
    agent = load_agent_directives()



    parts = []
    if user and user != DEFAULT_USER_MD.strip():
        parts.append(f"### User Profile\n{user}")
    if memory and memory != DEFAULT_MEMORY_MD.strip():
        parts.append(f"### Long-Term Memory\n{memory}")
    if agent and agent != DEFAULT_AGENT_MD.strip():
        parts.append(f"### Agent Directives\n{agent}")

    return "\n\n".join(parts) if parts else ""




def update_user_profile(new_content: str):
    """Overwrite the user profile with new content."""
    init_memory()
    with _reflect_lock:
        try:
            with open(USER_FILE, "w", encoding="utf-8") as f:
                f.write(new_content)
        except IOError:
            pass




def update_memory(new_content: str):
    """Overwrite the long-term memory with new content."""
    init_memory()
    with _reflect_lock:
        try:
            with open(MEMORY_FILE, "w", encoding="utf-8") as f:
                f.write(new_content)
        except IOError:
            pass


def update_agent_directives(new_content: str):
    """Overwrite the agent directives with new content."""
    init_memory()
    with _reflect_lock:
        try:
            with open(AGENT_FILE, "w", encoding="utf-8") as f:
                f.write(new_content)
        except IOError:
            pass










def append_to_memory(entry: str):
    """Append an entry to the long-term memory file."""
    init_memory()
    with _reflect_lock:
        try:
            with open(MEMORY_FILE, "a", encoding="utf-8") as f:
                f.write(f"\n- {entry}")
        except IOError:
            pass


def reflect_on_exchange(user_text: str, agent_text: str, tool_calls: list | None = None):
    """Analyze a conversation exchange and update memory files if noteworthy.

    This is called after each exchange. It applies cooldown to avoid
    excessive file writes. Updates are appended incrementally.
    """
    global _last_reflection
    now = time.time()
    if now - _last_reflection < REFLECTION_COOLDOWN:
        return

    _last_reflection = now

    user_lower = user_text.lower()



    
    name_patterns = [
        "my name is", "i'm", "i am", "call me", "i'm called",
    ]
    for pat in name_patterns:
        if pat in user_lower:
            idx = user_lower.index(pat) + len(pat)
            name_part = user_text[idx:].strip().split()[0:2]
            name = " ".join(name_part).strip(".,!?")
            if name and len(name) > 1:
                _update_user_name(name)
            break



    
    if any(w in user_lower for w in ["i like", "i love", "i prefer", "favorite"]):
        _append_user_preference(user_text)
    elif any(w in user_lower for w in ["i don't like", "i hate", "i dislike"]):
        _append_user_aversion(user_text)




    if tool_calls:
        tools_used = [tc.get("name", "") for tc in tool_calls]
        if tools_used:
            entry = f"Used {', '.join(tools_used)} for: {user_text[:60]}"
            append_to_memory(entry)


def _update_user_name(name: str):
    """Update the user's name in user.md."""
    try:
        content = load_user_profile()
        lines = content.split("\n")
        updated = False
        for i, line in enumerate(lines):
            if line.strip().startswith("- Name:"):
                lines[i] = f"- Name: {name}"
                updated = True
                break
        if not updated:
            lines.append(f"- Name: {name}")
        update_user_profile("\n".join(lines))
    except Exception:
        pass



def _append_user_preference(text: str):
    """Add a preference to user.md."""
    try:
        content = load_user_profile()
        lines = content.split("\n")



        
        pref_idx = -1
        for i, line in enumerate(lines):
            if "Preferences" in line or "preferences" in line:
                pref_idx = i
                break

        if pref_idx >= 0:

            
            insert_idx = pref_idx + 1
            while insert_idx < len(lines) and lines[insert_idx].startswith("- "):
                insert_idx += 1
            lines.insert(insert_idx, f"- Likes: {text[:80]}")
        else:
            lines.append(f"\n## Preferences\n- Likes: {text[:80]}")

        update_user_profile("\n".join(lines))
    except Exception:
        pass


def _append_user_aversion(text: str):
    """Add an aversion to user.md."""
    try:
        content = load_user_profile()
        lines = content.split("\n")

        pref_idx = -1
        for i, line in enumerate(lines):
            if "Preferences" in line or "preferences" in line:
                pref_idx = i
                break

        if pref_idx >= 0:
            insert_idx = pref_idx + 1
            while insert_idx < len(lines) and lines[insert_idx].startswith("- "):
                insert_idx += 1
            lines.insert(insert_idx, f"- Dislikes: {text[:80]}")
        else:
            lines.append(f"\n## Preferences\n- Dislikes: {text[:80]}")

        update_user_profile("\n".join(lines))
    except Exception:
        pass




init_memory()
