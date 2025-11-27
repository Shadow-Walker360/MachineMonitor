import psutil

def scan_active_connections():
    """
    Returns a list of active network connections
    Each connection includes: local_address, remote_address, status, pid
    """
    conns = []
    for conn in psutil.net_connections():
        conns.append({
            "local_address": f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else None,
            "remote_address": f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else None,
            "status": conn.status,
            "pid": conn.pid
        })
    return conns

def get_top_bandwidth_processes(n=5):
    """
    Returns top n processes by network I/O (bytes sent + received)
    """
    net_stats = []
    for p in psutil.process_iter(['pid', 'name']):
        try:
            io = p.io_counters()
            net_stats.append({
                "pid": p.info['pid'],
                "name": p.info['name'],
                "read_bytes": io.read_bytes,
                "write_bytes": io.write_bytes
            })
        except Exception:
            continue
    net_stats.sort(key=lambda x: x['read_bytes'] + x['write_bytes'], reverse=True)
    return net_stats[:n]

if __name__ == "__main__":
    print(scan_active_connections())
    print(get_top_bandwidth_processes())
