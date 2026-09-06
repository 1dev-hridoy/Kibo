"""
Macro tools — record, replay, and manage action sequences.
"""


def start_macro_recording(name):
    """Start recording a macro.
    
    Args:
        name: Name for the macro
    """
    from agent.core.macros import start_recording
    return start_recording(name)


def stop_macro_recording():
    """Stop recording and save the macro."""
    from agent.core.macros import stop_recording
    return stop_recording()


def replay_macro(name):
    """Replay a saved macro.
    
    Args:
        name: Name of the macro to replay
    """
    from agent.core.macros import replay_macro
    return replay_macro(name)


def list_macros():
    """List all saved macros."""
    from agent.core.macros import list_macros
    return list_macros()


def delete_macro(name):
    """Delete a saved macro.
    
    Args:
        name: Name of the macro to delete
    """
    from agent.core.macros import delete_macro
    return delete_macro(name)


def get_macro_status():
    """Get current recording status."""
    from agent.core.macros import get_recording_status
    return get_recording_status()
