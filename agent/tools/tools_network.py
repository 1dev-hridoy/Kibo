"""
Network security tool wrappers — scanning and listeners.
"""

import needle

from agent.runner.network_scan import (
    local_network_scan as _network_scan,
    subnet_port_sweep as _port_sweep,
    local_port_scan as _port_scan,
    list_local_listeners as _listeners,
)





@needle.tool
def local_network_scan() -> str:
    """Discover all active devices on your local network subnet.
    Uses parallel ICMP pings to scan 254 hosts in ~3 seconds.
    Returns IP addresses and hostnames of live devices.
    Use for: finding devices on your WiFi/network, network inventory."""
    print("[Tool] local_network_scan()")
    result = _network_scan()
    hosts = result.get("hosts", [])
    if not hosts:
        return f"No devices found on subnet {result['subnet']}.0/24."
    lines = [f"Subnet: {result['subnet']}.0/24 — {len(hosts)} devices found:\n"]
    for h in hosts:
        name = f" ({h['hostname']})" if h["hostname"] else ""
        lines.append(f"  {h['ip']}{name}")
    return "\n".join(lines)





@needle.tool
def subnet_port_sweep(port: int = 80) -> str:
    """Sweep your entire local subnet to find which hosts have a specific port open.
    Use for: finding web servers (port 80/443), SSH servers (port 22),
    or any service running on your network."""
    print(f"[Tool] subnet_port_sweep({port})")
    result = _port_sweep(port)
    hosts = result.get("open_hosts", [])
    if not hosts:
        return f"No hosts found with port {port} open."
    lines = [f"Port {port} open on {len(hosts)} hosts:"]
    for ip in hosts:
        lines.append(f"  {ip}")
    return "\n".join(lines)




@needle.tool
def local_port_scan(ip: str, ports: str = "") -> str:
    """Scan up to 100 ports on a target IP address.
    Use for: finding open services on a specific machine.
    Ports default to common services (22, 80, 443, 3306, etc.).
    Optionally pass a comma-separated list of specific ports."""
    print(f"[Tool] local_port_scan('{ip}', '{ports}')")
    port_list = None
    if ports:
        try:
            port_list = [int(p.strip()) for p in ports.split(",") if p.strip()]
        except ValueError:
            return "Error: ports must be comma-separated numbers."
    result = _port_scan(ip, port_list)
    open_ports = result.get("open_ports", [])
    if not open_ports:
        return f"No open ports found on {ip}."
    lines = [f"Open ports on {ip}:"]
    for p in open_ports:
        lines.append(f"  Port {p['port']}: {p['service']}")
    return "\n".join(lines)




@needle.tool
def list_local_listeners() -> str:
    """List all active listening ports on this PC.
    Use for: checking what services are running, debugging network issues,
    finding which ports are in use."""
    print("[Tool] list_local_listeners()")
    listeners = _listeners()
    if not listeners:
        return "No listening ports found."
    lines = [f"{len(listeners)} listening ports:\n"]
    for entry in listeners:
        proto = entry.get("protocol", "")
        addr = entry.get("local_address", "")
        proc = entry.get("process", "")
        pid = entry.get("pid", "")
        proc_info = ""
        if proc:
            proc_info = f" ({proc})"
        elif pid:
            proc_info = f" (PID: {pid})"
        lines.append(f"  {proto} {addr}{proc_info}")
    return "\n".join(lines)
