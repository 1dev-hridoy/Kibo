def sys_info():


    try:
        import shutil
        free = shutil.disk_usage("/").free // (1024 ** 3)
        parts = [f"{free}G free"]
    except Exception:



        parts = []
    try:

        import glob
        bats = glob.glob("/sys/class/power_supply/BAT*/capacity")
        if bats:
            with open(bats[0]) as f:
                parts.append(f"{f.read().strip()}%")


    except Exception:
        pass
    try:
        with open("/proc/loadavg") as f:
            load = float(f.read().split()[0])
        import os
        cores = os.cpu_count() or 1
        parts.append(f"cpu {int(load / cores * 100)}%")




    except Exception:
        pass
    try:
        total = avail = 0
        with open("/proc/meminfo") as f:
            for line in f:
                if line.startswith("MemTotal:"):
                    total = int(line.split()[1])
                elif line.startswith("MemAvailable:"):
                    avail = int(line.split()[1])
        if total:
            parts.append(f"ram {int((total - avail) / total * 100)}%")


            
    except Exception:
        pass
    return " · ".join(parts) if parts else "idle"
