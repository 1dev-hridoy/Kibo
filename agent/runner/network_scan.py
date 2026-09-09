"""
Network scanning utilities — subnet host discovery, port sweeping,
concurrent port scanning, and local listener enumeration.
"""

import os
import socket
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed


def _get_local_subnet() -> str:
    """Get the local subnet prefix (e.g. '192.168.1')."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ".".join(ip.split(".")[:3])
    except Exception:
        return "192.168.1"


def _ping_host(ip: str, timeout: float = 0.3) -> str | None:
    """Ping a single host. Returns IP if alive, None otherwise."""
    try:
        param = "-c" if os.name != "nt" else "-n"
        timeout_param = "-W" if os.name != "nt" else "-w"
        ms = str(int(timeout * 1000 if os.name == "nt" else timeout))
        argv = ["ping", param, "1", timeout_param, ms, ip]
        res = subprocess.run(argv, capture_output=True, text=True,
                             timeout=timeout + 0.5)
        if res.returncode == 0:
            return ip
    except (subprocess.TimeoutExpired, Exception):
        pass
    return None





def _resolve_hostname(ip: str) -> str:
    """Reverse DNS lookup for an IP."""
    try:
        return socket.gethostbyaddr(ip)[0]
    except (socket.herror, socket.gaierror, OSError):
        return ""

    


def _check_port(ip: str, port: int, timeout: float = 0.3) -> tuple[str, int] | None:
    """Check if a single port is open on a host."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(timeout)
            if s.connect_ex((ip, port)) == 0:
                return (ip, port)
    except (socket.timeout, OSError):
        pass
    return None





SERVICE_NAMES = {
    21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP", 53: "DNS",
    80: "HTTP", 110: "POP3", 111: "RPCBind", 135: "MSRPC",
    139: "NetBIOS", 143: "IMAP", 443: "HTTPS", 445: "SMB",
    993: "IMAPS", 995: "POP3S", 1433: "MSSQL", 1521: "Oracle",
    3306: "MySQL", 3389: "RDP", 5432: "PostgreSQL", 5900: "VNC",
    6379: "Redis", 8080: "HTTP-Alt", 8443: "HTTPS-Alt",
    27017: "MongoDB", 50000: "SAP",
}


def _scan_port(ip: str, port: int, timeout: float = 0.5) -> dict | None:
    """Scan a single port and return service info if open."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(timeout)
            if s.connect_ex((ip, port)) == 0:
                return {"port": port, "service": SERVICE_NAMES.get(port, "unknown")}
    except (socket.timeout, OSError):
        pass
    return None






def local_network_scan() -> dict:
    """Scan the local subnet for active hosts using parallel ICMP pings.

    Returns dict with 'subnet', 'hosts' (list of {ip, hostname}).
    """
    subnet = _get_local_subnet()
    ips = [f"{subnet}.{i}" for i in range(1, 255)]

    alive = []
    with ThreadPoolExecutor(max_workers=80) as pool:
        futures = {pool.submit(_ping_host, ip): ip for ip in ips}
        for future in as_completed(futures):
            result = future.result()
            if result:
                hostname = _resolve_hostname(result)
                alive.append({"ip": result, "hostname": hostname})

    alive.sort(key=lambda h: tuple(int(x) for x in h["ip"].split(".")))
    return {"subnet": subnet, "hosts": alive}


def subnet_port_sweep(port: int) -> dict:
    """Sweep the entire local subnet checking which hosts have a specific port open.

    Returns dict with 'port', 'open_hosts' (list of IPs).
    """
    subnet = _get_local_subnet()
    ips = [f"{subnet}.{i}" for i in range(1, 255)]

    open_hosts = []
    with ThreadPoolExecutor(max_workers=80) as pool:
        futures = {pool.submit(_check_port, ip, port): ip for ip in ips}
        for future in as_completed(futures):
            result = future.result()
            if result:
                open_hosts.append(result[0])

    open_hosts.sort(key=lambda ip: tuple(int(x) for x in ip.split(".")))
    return {"port": port, "open_hosts": open_hosts}





def local_port_scan(ip: str, ports: list[int] | None = None) -> dict:
    """Scan up to 100 ports concurrently on a target IP.

    Returns dict with 'ip', 'open_ports' (list of {port, service}).
    """
    if ports is None:
        ports = sorted(SERVICE_NAMES.keys())
    ports = ports[:100]

    open_ports = []
    with ThreadPoolExecutor(max_workers=50) as pool:
        futures = {pool.submit(_scan_port, ip, p): p for p in ports}
        for future in as_completed(futures):
            result = future.result()
            if result:
                open_ports.append(result)

    open_ports.sort(key=lambda x: x["port"])
    return {"ip": ip, "open_ports": open_ports}







def list_local_listeners() -> list[dict]:
    """List active listening ports on the local machine.

    Returns list of dicts with 'protocol', 'local_address', 'pid', 'process'.
    """
    listeners = []

    try:
        if os.name == "nt":
            res = subprocess.run(
                ["netstat", "-ano"],
                capture_output=True, text=True, timeout=10, errors="replace")
            for line in res.stdout.splitlines():
                if "LISTENING" in line:
                    parts = line.split()
                    if len(parts) >= 5:
                        listeners.append({
                            "protocol": parts[0],
                            "local_address": parts[3],
                            "pid": parts[4],
                            "process": "",
                        })



        else:
            res = subprocess.run(
                ["ss", "-tlnp"],
                capture_output=True, text=True, timeout=10, errors="replace")
            if res.returncode != 0:
                res = subprocess.run(
                    ["netstat", "-tlnp"],
                    capture_output=True, text=True, timeout=10, errors="replace")



            for line in res.stdout.splitlines()[1:]:
                parts = line.split()
                if len(parts) >= 4:
                    listeners.append({
                        "protocol": parts[0],
                        "local_address": parts[3],
                        "pid": "",
                        "process": parts[-1] if len(parts) > 5 else "",
                    })


    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        pass

    

    return listeners
