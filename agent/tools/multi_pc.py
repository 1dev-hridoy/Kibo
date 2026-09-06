"""
Multi-PC tools — register, switch, and execute on remote computers.
"""


def register_remote_pc(name, host, port=5000, username="", key_path=""):
    """Register a remote PC for control.
    
    Args:
        name: Friendly name (e.g., "laptop", "office-pc")
        host: IP address or hostname
        port: Kibo web API port (default 5000)
        username: SSH username
        key_path: Path to SSH key file
    """
    from agent.core.multi_pc import register_pc
    return register_pc(name, host, port, username, key_path)


def unregister_remote_pc(name):
    """Remove a registered PC."""
    from agent.core.multi_pc import unregister_pc
    return unregister_pc(name)


def list_remote_pcs():
    """List all registered PCs."""
    from agent.core.multi_pc import list_pcs
    return list_pcs()


def switch_to_pc(name):
    """Switch control to a different PC.
    
    Args:
        name: PC name or "local" for this machine
    """
    from agent.core.multi_pc import switch_pc
    return switch_pc(name)


def get_current_pc():
    """Get the currently active PC info."""
    from agent.core.multi_pc import get_active_pc
    info = get_active_pc()
    return f"Active PC: {info['name']} ({info['host']}:{info['port']})"


def ping_remote_pc(name):
    """Check if a PC is online.
    
    Args:
        name: PC name to check
    """
    from agent.core.multi_pc import ping_pc
    return ping_pc(name)


def execute_on_remote_pc(pc_name, command):
    """Execute a shell command on a remote PC.
    
    Args:
        pc_name: Target PC name
        command: Shell command to execute
    """
    from agent.core.multi_pc import execute_on_pc
    return execute_on_pc(pc_name, command)
