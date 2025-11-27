import psutil
import time
from backend.database import log_system
from backend.ai_analysis import analyze_system, predict_issues, optimize_performance, generate_report

def get_system_snapshot():
    # Processes info
    processes = []
    for p in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
        processes.append(p.info)

    # Disk usage and health
    disk_info = {}
    for part in psutil.disk_partitions():
        usage = psutil.disk_usage(part.mountpoint)
        disk_info[part.device] = {
            "usage": usage.percent,
            "total": usage.total,
            "used": usage.used,
            "free": usage.free
        }
    # For health, assume all healthy for now
    health_info = {part.device: "Healthy" for part in psutil.disk_partitions()}
    disk_info['health'] = health_info

    # Network stats
    net_connections = []
    for conn in psutil.net_connections():
        net_connections.append({
            "fd": conn.fd,
            "family": str(conn.family),
            "type": str(conn.type),
            "local_address": str(conn.laddr),
            "remote_address": str(conn.raddr) if conn.raddr else "",
            "status": conn.status
        })

    snapshot = {
        "cpu": psutil.cpu_percent(interval=1),
        "ram": psutil.virtual_memory().percent,
        "disk": disk_info,
        "network": net_connections,
        "processes": processes
    }
    return snapshot

def run_monitor(interval=5):
    while True:
        snapshot = get_system_snapshot()
        log_system(snapshot)

        # AI Analysis
        ai_result = analyze_system(snapshot)
        predicted_issues = predict_issues([])  # Pass historical data if available
        optimizations = optimize_performance(snapshot)
        report = generate_report(snapshot)
        # Log AI analysis
        from backend.database import log_ai
        log_ai(ai_result, optimizations, report)

        time.sleep(interval)

if __name__ == "__main__":
    run_monitor()
