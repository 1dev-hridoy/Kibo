"""
WebSocket terminal — PTY access via xterm.js in the browser.
"""

import os
import pty
import select
import subprocess
import threading
import json
import signal


class PTYSession:
    """Manages a single PTY session."""

    def __init__(self, session_id, cols=80, rows=24):
        self.session_id = session_id
        self.master = None
        self.pid = None
        self.cols = cols
        self.rows = rows
        self.running = False

    def start(self):
        """Start the PTY process."""
        self.pid, self.master = pty.fork()
        if self.pid == 0:
     
            os.environ["TERM"] = "xterm-256color"
            os.execvp("/bin/bash", ["/bin/bash", "--login"])
        else:
       
            self.running = True
 
            import fcntl
            import struct
            winsize = struct.pack("HHHH", self.rows, self.cols, 0, 0)
            fcntl.ioctl(self.master, _TIOCSWINSZ, winsize)

    def read(self, size=4096, timeout=0.01):
        """Read from PTY."""
        if not self.master:
            return ""
        try:
            r, _, _ = select.select([self.master], [], [], timeout)
            if r:
                return os.read(self.master, size).decode("utf-8", errors="replace")
        except Exception:
            pass
        return ""

    def write(self, data):
        """Write to PTY."""
        if self.master:
            os.write(self.master, data.encode())

    def resize(self, cols, rows):
        """Resize the PTY."""
        self.cols = cols
        self.rows = rows
        if self.master:
            import fcntl
            import struct
            winsize = struct.pack("HHHH", rows, cols, 0, 0)
            fcntl.ioctl(self.master, _TIOCSWINSZ, winsize)

    def close(self):
        """Close the PTY."""
        self.running = False
        if self.master:
            try:
                os.close(self.master)
            except Exception:
                pass
        if self.pid:
            try:
                os.kill(self.pid, signal.SIGTERM)
                os.waitpid(self.pid, os.WNOHANG)
            except Exception:
                pass




import struct
_TIOCSWINSZ = 0x5414





_sessions = {}
_sessions_lock = threading.Lock()


def create_session(session_id=None, cols=80, rows=24):
    """Create a new PTY session."""
    if not session_id:
        import secrets
        session_id = secrets.token_hex(8)

    with _sessions_lock:
        if session_id in _sessions:
            return session_id, "Session already exists"

        session = PTYSession(session_id, cols, rows)
        session.start()
        _sessions[session_id] = session
        return session_id, f"Session {session_id} created"


def write_to_session(session_id, data):
    """Write input to a session."""
    with _sessions_lock:
        session = _sessions.get(session_id)
    if session:
        session.write(data)
        return True
    return False


def read_from_session(session_id, size=4096):
    """Read output from a session."""
    with _sessions_lock:
        session = _sessions.get(session_id)
    if session:
        return session.read(size)
    return ""


def resize_session(session_id, cols, rows):
    """Resize a session."""
    with _sessions_lock:
        session = _sessions.get(session_id)
    if session:
        session.resize(cols, rows)
        return True
    return False


def close_session(session_id):
    """Close a session."""
    with _sessions_lock:
        session = _sessions.pop(session_id, None)
    if session:
        session.close()
        return True
    return False


def list_sessions():
    """List active sessions."""
    with _sessions_lock:
        return list(_sessions.keys())
