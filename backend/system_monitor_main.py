import time
from backend.system_monitor_main import get_cpu_usage, get_ram_usage
from backend.system_monitor import get_disk_usage, get_disk_health
from backend.process_monitor import list_processes
from backend.network_monitor import scan_active_connections
from backend.ai_analysis import analyze_system, predict_issues, optimize_performance, detect_security_threats, generate_report
from backend.database import log_system_snapshot, log_ai_analysis

def monitor_and_log(interval=5):
    """
    Monitors system metrics, runs AI analysis, and logs to MongoDB.
    Runs in a continuous loop.
    """
    while True:
        # 1. Gather system metrics
        cpu = get_cpu_usage()
        ram = get_ram_usage()
        disk = get_disk_usage()
        disk_health = get_disk_health()
        processes = list_processes()
        network = scan_active_connections()

        # 2. Log system snapshot to MongoDB
        log_system_snapshot(cpu, ram, {"usage": disk, "health": disk_health}, network, processes)

        # 3. Run AI analysis
        snapshot_data = {
            "cpu": cpu,
            "ram": ram,
            "disk": {"usage": disk, "health": disk_health},
            "network": network,
            "processes": processes
        }
        analysis = analyze_system(snapshot_data)
        predictions = predict_issues([snapshot_data])  # we can pass history if available
        optimizations = optimize_performance(snapshot_data)
        threats = detect_security_threats(network)
        report = generate_report(snapshot_data)

        # 4. Log AI analysis to MongoDB
        log_ai_analysis(analysis, predictions, optimizations, threats, report)

        # 5. Print to console for quick feedback (optional)
        print(f"CPU: {cpu}%, RAM: {ram}%, Disk: {disk}%, Network connections: {len(network)}")
        print(f"AI Status: {analysis['status']}, Recommendations: {optimizations['suggestions']}\n")

        time.sleep(interval)

if __name__ == "__main__":
    monitor_and_log()
