import os
import subprocess
import sys


HOME = os.environ.get("KIBO_HOME") or os.path.join(os.path.expanduser("~"), "kibo")
ENV = os.environ.get("KIBO_ENV") or os.path.expanduser("~/.config/kibo/.env")


def _python():
    if os.name == "nt":
        return os.path.join(HOME, ".venv", "Scripts", "python.exe")
    return os.path.join(HOME, "venv", "bin", "python")



def _load_env():
    if not os.path.isfile(ENV):
        return
    try:
        with open(ENV) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, _, val = line.partition("=")
                os.environ.setdefault(key.strip(), val.strip().strip("'\""))
    except OSError:
        pass




def running():
    try:
        out = subprocess.run(["pgrep", "-af", "[-]m agent"],
                             capture_output=True, text=True).stdout
    except (OSError, subprocess.SubprocessError):
        return []
    return [l for l in out.splitlines() if l.strip()]




def cmd_help():
    print()
    print("  Kibo - your PC, controlled by chat")
    print()
    print("    kibo                  show this help")
    print("    kibo chat             interactive terminal chat")
    print("    kibo web              browser UI on 127.0.0.1:5000")
    print("    kibo telegram         telegram bot + widget")
    print("    kibo all              web + telegram")
    print("    kibo start <mode>     start a mode in the background")
    print("    kibo stop             stop every kibo process")
    print("    kibo restart <mode>   stop, then start again")
    print("    kibo status           show what is running")
    print("    kibo logs [n]         tail the last n log lines")
    print("    kibo update           git pull and reinstall")
    print()
    print("    Home: %s" % HOME)
    print()






def cmd_run(mode):
    _load_env()
    try:
        os.chdir(HOME)
    except OSError:
        print("  Kibo is not installed at %s" % HOME)
        return 1
    os.execv(_python(), [_python(), "-m", "agent"] + mode)
    return 0




def cmd_start(mode):
    if running():
        print("  Kibo is already running. Try: kibo stop")
        return 0
    _load_env()
    try:




        os.chdir(HOME)
    except OSError:
        print("  Kibo is not installed at %s" % HOME)
        return 1
    logdir = os.path.join(HOME, "logs")



    try:
        os.makedirs(logdir, exist_ok=True)
    except OSError:
        logdir = None
    out = open(os.path.join(logdir, "kibo.log"), "ab") if logdir else subprocess.DEVNULL
    subprocess.Popen([_python(), "-m", "agent"] + mode,
                     cwd=HOME, stdout=out, stderr=subprocess.STDOUT,
                     stdin=subprocess.DEVNULL, start_new_session=True)
    if running():
        print("  Kibo started (%s)" % HOME)
        return 0
    print("  Kibo did not start - check: kibo logs")
    return 1





def cmd_stop():
    if not running():
        print("  Kibo is not running.")
        return 0
    try:
        subprocess.run(["pkill", "-f", "[-]m agent"], check=False)
    except OSError:
        pass
    print("  Kibo stopped.")
    return 0




def cmd_status():
    procs = running()
    if procs:
        print("  Kibo is running")
        for p in procs:
            print("    %s" % p)
    else:
        print("  Kibo is not running")
    return 0








def cmd_logs(count):
    logdir = os.path.join(HOME, "logs")
    files = []
    try:
        files = [os.path.join(logdir, f) for f in sorted(os.listdir(logdir))
                 if f.endswith(".log")]
    except OSError:
        pass
    if not files:
        print("  no logs yet")
        return 0
    subprocess.run(["tail", "-n", str(count), *files])
    return 0




def cmd_update():
    try:
        os.chdir(HOME)
    except OSError:
        print("  Kibo is not installed at %s" % HOME)
        return 1
    subprocess.run(["git", "pull", "--quiet"])
    subprocess.run([_python(), "-m", "pip", "install", "--quiet", "-e", "."])
    print("  Kibo updated.")
    return 0


COMMANDS = {
    "help": lambda a: cmd_help(),
    "chat": lambda a: cmd_run([]),
    "web": lambda a: cmd_run(["web"]),
    "telegram": lambda a: cmd_run(["telegram"]),
    "all": lambda a: cmd_run(["all"]),
    "start": lambda a: cmd_start(a[:1] or ["telegram"]),
    "stop": lambda a: cmd_stop(),
    "restart": lambda a: (cmd_stop(), cmd_start(a[:1] or ["telegram"]))[1],
    "status": lambda a: cmd_status(),
    "logs": lambda a: cmd_logs(a[:1] or ["40"]),
    "update": lambda a: cmd_update(),
}




def main():
    args = sys.argv[1:]
    if not args or args[0] in ("help", "-h", "--help"):
        cmd_help()
        return 0
    action = COMMANDS.get(args[0].lower())
    if action is None:
        print("  Unknown command: %s" % args[0])
        cmd_help()
        return 1
    return action(args[1:]) or 0


if __name__ == "__main__":
    sys.exit(main())
