import psutil
from backend.database import log_ai

def scan_network_connections():
    connections = []
    for conn in psutil.net_connections(kind='inet'):
        connections.append({
            "fd": conn.fd,
            "type": str(conn.type),
            "local": str(conn.laddr),
            "remote": str(conn.raddr) if conn.raddr else "",
            "status": conn.status
        })
    return connections

def get_network_usage():
    net = psutil.net_io_counters()
    usage = {"bytes_sent": net.bytes_sent, "bytes_recv": net.bytes_recv}
    log_ai({"network_usage": usage})
    return usage
