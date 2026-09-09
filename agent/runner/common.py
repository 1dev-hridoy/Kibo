"""Shared helpers: run(), run_cmd(), run_cmd_json(), powershell(), _find(), _pkg_hint(),
CREATE_NO_WINDOW, StatefulShell."""

import base64
import json
import os
import queue
import shutil
import subprocess
import threading
import time

from agent.config import (
    CMD_TIMEOUT, IS_WINDOWS, IS_MACOS, IS_LINUX, LINUX_DISTRO,
)

CREATE_NO_WINDOW = 0x08000000 if IS_WINDOWS else 0


def _find(*names):
    """Return the first existing binary among names, else None."""
    for n in names:
        path = shutil.which(n)
        if path:
            return path
    return None


def _pkg_hint(apt, dnf, pacman, zypper, apk):
    """Return the distro-appropriate install command for a package."""
    if IS_LINUX:
        hint = {"apt": apt, "dnf": dnf, "pacman": pacman,
                "zypper": zypper, "apk": apk}
        mgr = {"ubuntu": "apt", "debian": "apt", "linuxmint": "apt",
               "fedora": "dnf", "rhel": "dnf", "centos": "dnf",
               "arch": "pacman", "manjaro": "pacman", "endeavouros": "pacman",
               "cachyos": "pacman", "opensuse": "zypper",
               "alpine": "apk"}.get(LINUX_DISTRO)
        if mgr:
            return hint.get(mgr, "")
    return ""


def run(argv, timeout: int = CMD_TIMEOUT) -> str:
    """Execute a native command and return its output (generic helper)."""
    try:
        kwargs = {}
        if IS_WINDOWS:
            kwargs["creationflags"] = CREATE_NO_WINDOW
        res = subprocess.run(argv, capture_output=True, text=True,
                             errors="replace", timeout=timeout, **kwargs)
        if res.returncode == 0:
            return res.stdout.strip() if res.stdout.strip() else "Success"
        err = res.stderr.strip() or res.stdout.strip() or f"Exit code {res.returncode}"
        return f"Error ({argv[0]}): {err}"
    except subprocess.TimeoutExpired:
        return f"Error ({argv[0]}): Timed out after {timeout}s."
    except (FileNotFoundError, PermissionError, OSError) as e:
        return f"Error ({argv[0]}): {e}"


# Convenience aliases for user-defined custom tools
run_cmd = run


def run_cmd_json(argv, timeout: int = CMD_TIMEOUT):
    """Execute a command and parse its JSON output."""
    res = run(argv, timeout)
    try:
        return json.loads(res)
    except (json.JSONDecodeError, TypeError):
        return res


if IS_WINDOWS:
    def powershell(script: str, timeout: int = 60) -> str:
        """Run a PowerShell script (base64-encoded, windowless). Returns stdout."""
        encoded = base64.b64encode(script.encode("utf-16-le")).decode("ascii")
        try:
            res = subprocess.run(
                ["powershell", "-NoProfile", "-NonInteractive",
                 "-ExecutionPolicy", "Bypass", "-EncodedCommand", encoded],
                capture_output=True, text=True, errors="replace",
                timeout=timeout, creationflags=CREATE_NO_WINDOW)
            if res.returncode == 0:
                return res.stdout.strip()
            err = res.stderr.strip() or f"Exit code {res.returncode}"
            return f"Error: {err}"
        except subprocess.TimeoutExpired:
            return f"Error: PowerShell timed out after {timeout}s."
        except (FileNotFoundError, OSError) as e:
            return f"Error: PowerShell unavailable ({e})."
else:
    def powershell(script: str, timeout: int = 60) -> str:
        return "Error: PowerShell is only available on Windows."


# ═══════════════════════════════════════════════════════════════════════
# STATEFUL PERSISTENT SHELL
# ═══════════════════════════════════════════════════════════════════════

_FORBIDDEN_COMMANDS = ["rm -rf /", "rm -f /", "mkfs", "dd if=", ":(){:|:&};:"]


class StatefulShell:
    """A persistent background shell that maintains directory changes
    and environment variables across multiple command invocations.

    On Unix: runs a persistent bash process with sentinel-based I/O.
    On Windows: tracks directory state and executes via PowerShell/cmd.
    """




    def __init__(self):
        self.process = None
        self._stdout_queue: queue.Queue = queue.Queue()
        self._stderr_queue: queue.Queue = queue.Queue()
        self._stdout_thread: threading.Thread | None = None
        self._stderr_thread: threading.Thread | None = None
        self.current_directory = os.path.expanduser("~")
        self._lock = threading.Lock()
        self._init_shell()



    def _init_shell(self):
        if IS_WINDOWS:
            return

        try:
            shell_bin = shutil.which("bash") or shutil.which("sh")
            if not shell_bin:
                return

            self.process = subprocess.Popen(
                [shell_bin],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                cwd=self.current_directory,
            )

            def _reader(stream, q):
                try:
                    for line in iter(stream.readline, ""):
                        q.put(line)
                except (ValueError, OSError):
                    pass
                finally:
                    try:
                        stream.close()
                    except (ValueError, OSError):
                        pass

            self._stdout_thread = threading.Thread(
                target=_reader, args=(self.process.stdout, self._stdout_queue),
                daemon=True)
            self._stderr_thread = threading.Thread(
                target=_reader, args=(self.process.stderr, self._stderr_queue),
                daemon=True)
            self._stdout_thread.start()
            self._stderr_thread.start()
        except Exception as e:
            print(f"[StatefulShell] init failed: {e}")

    def _check_forbidden(self, cmd: str) -> str | None:
        for token in _FORBIDDEN_COMMANDS:
            if token in cmd:
                return f"Error: Command blocked — forbidden token '{token}'."
        return None



    def execute(self, cmd: str, timeout: int = 30) -> str:
        """Execute a command in the persistent shell. Maintains cd/env across calls."""
        cmd = cmd.strip()
        if not cmd:
            return "Error: No command provided."

        forbidden = self._check_forbidden(cmd)
        if forbidden:
            return forbidden

        with self._lock:
            if IS_WINDOWS:
                return self._execute_windows(cmd, timeout)
            return self._execute_unix(cmd, timeout)

    def _execute_windows(self, cmd: str, timeout: int) -> str:
        ps_script = (
            f"$ErrorActionPreference = 'Continue'\n"
            f"{cmd}\n"
            f"Write-Output '__KIBO_PWD__:{(Get-Location).Path}'"
        )



        try:
            res = subprocess.run(
                ["powershell.exe", "-NoProfile", "-NonInteractive",
                 "-Command", ps_script],
                capture_output=True, text=True, errors="replace",
                cwd=self.current_directory, timeout=timeout,
                creationflags=CREATE_NO_WINDOW,
            )
            output_lines = res.stdout.splitlines(keepends=True)
            clean = []
            for line in output_lines:
                stripped = line.strip()
                if stripped.startswith("__KIBO_PWD__:"):
                    new_dir = stripped.split(":", 1)[1].strip()
                    if os.path.isdir(new_dir):
                        self.current_directory = new_dir
                else:
                    clean.append(line)

            result = "".join(clean)
            if res.stderr and res.stderr.strip():
                result += "\n[stderr]\n" + res.stderr
            return result.strip() or "Command executed (no output)."
        except subprocess.TimeoutExpired:
            return f"Error: Command timed out after {timeout}s."
        except Exception as e:
            return f"Error: {e}"


        

    def _execute_unix(self, cmd: str, timeout: int) -> str:
        if not self.process or self.process.poll() is not None:
            self._init_shell()
            if not self.process:
                return "Error: Could not start shell."



     
        for q in (self._stdout_queue, self._stderr_queue):
            while not q.empty():
                try:
                    q.get_nowait()
                except queue.Empty:
                    break

        sentinel = f"__KIBO_DONE_{int(time.time() * 1000)}__"
        full_cmd = f"{cmd}\necho __KIBO_PWD__$PWD\necho {sentinel}\necho {sentinel} >&2\n"

        try:
            self.process.stdin.write(full_cmd)
            self.process.stdin.flush()
        except (BrokenPipeError, OSError):
            self._init_shell()
            if not self.process:
                return "Error: Shell died and could not restart."
            try:
                self.process.stdin.write(full_cmd)
                self.process.stdin.flush()
            except (BrokenPipeError, OSError) as e:
                return f"Error: Cannot write to shell: {e}"

        stdout_buf, stderr_buf = [], []
        start = time.time()



        while time.time() - start < timeout:
            for buf, q in ((stdout_buf, self._stdout_queue),
                           (stderr_buf, self._stderr_queue)):
                while True:
                    try:
                        line = q.get_nowait()
                        buf.append(line)
                    except queue.Empty:
                        break

            if any(sentinel in l for l in stdout_buf):
                break
            time.sleep(0.03)

        stdout_clean = [l for l in stdout_buf if sentinel not in l]
        stderr_clean = [l for l in stderr_buf if sentinel not in l]




  
        if stdout_clean:
            last = stdout_clean[-1].strip()
            if last.startswith("__KIBO_PWD__"):
                pwd = last.split("__KIBO_PWD__", 1)[1].strip()
                if os.path.isdir(pwd):
                    self.current_directory = pwd
                    stdout_clean = stdout_clean[:-1]

        output = "".join(stdout_clean)
        if stderr_clean:
            output += "\n[stderr]\n" + "".join(stderr_clean)

        if not output.strip():
            if time.time() - start >= timeout:
                return f"Command timed out after {timeout}s."
            return "Command executed (no output)."

        return output


    

    def getcwd(self) -> str:
        return self.current_directory

    def close(self):
        if self.process and self.process.poll() is None:
            try:
                self.process.stdin.write("exit\n")
                self.process.stdin.flush()
                self.process.wait(timeout=3)
            except Exception:
                try:
                    self.process.kill()
                except Exception:
                    pass





_persistent_shell: StatefulShell | None = None
_shell_lock = threading.Lock()




def get_persistent_shell() -> StatefulShell:
    """Get or create the global persistent shell instance."""
    global _persistent_shell
    if _persistent_shell is None or _persistent_shell.process is None or _persistent_shell.process.poll() is not None:
        with _shell_lock:
            if _persistent_shell is None or _persistent_shell.process is None or _persistent_shell.process.poll() is not None:
                _persistent_shell = StatefulShell()
    return _persistent_shell


def run_persistent(cmd: str, timeout: int = 30) -> str:
    """Execute a command in the persistent shell. Maintains cd and env across calls."""
    return get_persistent_shell().execute(cmd, timeout)
