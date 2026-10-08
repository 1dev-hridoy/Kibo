import datetime
import json
import urllib.request


def _weather():


    try:
        req = urllib.request.Request(
            "https://wttr.in/?format=j1",
            headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.load(r)
        area = data.get("nearest_area", [{}])[0]
        place = area.get("areaName", [{}])[0].get("value", "here")
        cur = data.get("current_condition", [{}])[0]
        temp = cur.get("temp_C", "?")
        desc = cur.get("weatherDesc", [{}])[0].get("value", "")
        humid = cur.get("humidity", "?")
        today = (data.get("weather", [{}])[0])
        hi = today.get("maxtempC", "?")
        lo = today.get("mintempC", "?")


        return (f"{place}: {temp}C, {desc.lower()}, humidity {humid}%. "
                f"High {hi}, low {lo}.")
    except Exception:
        return "Weather unavailable (offline?)."



def _agenda():
    try:

        from agent.core.scheduler import _load_jobs
        _load_jobs()
        from agent.core import scheduler as _sched
        active = [j for j in _sched._jobs if j.get("active")]
        if not active:
            return "Nothing scheduled today."
        bits = []


        for j in active[:5]:
            label = j.get("label", "")
            if label.startswith("reminder:"):
                bits.append(label.split(":", 1)[1].replace("remind_", ""))
            elif label.startswith("briefing:"):
                continue
            else:
                bits.append(label)


        if not bits:
            return "Nothing scheduled today."
        return "Reminders active: " + ", ".join(bits) + "."
    except Exception:
        return ""


def build_briefing():


    now = datetime.datetime.now()
    greeting = ("Good morning" if now.hour < 12 else
                "Good afternoon" if now.hour < 17 else "Good evening")

    
    day = now.strftime("%A, %B %d")
    lines = [f"{greeting}! {day}.", _weather()]
    try:
        from agent.runner.battery import battery_status

        info = battery_status()
        if info:
            lines.append(
                f"Battery: {info.get('percent')}% "
                f"({info.get('status', '').lower()}).")


            
        else:
            lines.append("On AC power.")
    except Exception:
        pass


    try:

        from agent.runner.disk import disk_usage
        disks = disk_usage()
        root = next((d for d in disks if d.get("mount") == "/"),
                    disks[0] if disks else None)
        if root:
            lines.append(
                f"Disk: {root.get('available')} free of {root.get('total')}.")
    except Exception:
        pass


    try:
        from agent.runner.processes import list_processes
        procs = sorted(list_processes(), key=lambda p: p.get("cpu", 0),
                       reverse=True)[:3]
        busy = ", ".join(
            f"{p.get('command', '').split()[0].split('/')[-1]} "
            f"{p.get('cpu', 0):.0f}%" for p in procs)
   
   
   
   
        if busy:
            lines.append(f"Busy processes: {busy}.")
    except Exception:
        pass
  
  
    agenda = _agenda()
    if agenda:
        lines.append(agenda)
    return "\n".join(lines)
