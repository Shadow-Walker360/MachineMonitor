import numpy as np
from sklearn.ensemble import IsolationForest
from backend.database import log_ai

# Maintain historical snapshots
history_data = []

def analyze_system(snapshot):
    """
    Detect anomalies in CPU, RAM, Disk usage using IsolationForest
    """
    global history_data
    cpu = snapshot.get("cpu", 0)
    ram = snapshot.get("ram", 0)
    disk_usage = snapshot.get("disk", {}).get("usage", 0)

    # Append to history
    history_data.append([cpu, ram, disk_usage])

    # Only run ML after at least 10 snapshots
    if len(history_data) > 10:
        clf = IsolationForest(contamination=0.1, random_state=42)
        clf.fit(history_data)
        pred = clf.predict([[cpu, ram, disk_usage]])
        status = "Normal" if pred[0] == 1 else "Anomaly"
    else:
        status = "Normal"

    recommendations = []
    if cpu > 85:
        recommendations.append("Close heavy CPU applications")
    if ram > 85:
        recommendations.append("Free up RAM")
    if disk_usage > 90:
        recommendations.append("Clean up disk space")

    result = {"status": status, "recommendations": recommendations}
    log_ai(result)  # store in MongoDB
    return result

def predict_issues(history):
    """
    Predict potential system issues based on historical data using trend analysis
    """
    if not history:
        return {"predicted_issues": []}
    
    latest = history[-1]
    issues = []
    if latest.get("cpu", 0) > 80:
        issues.append("CPU overload risk")
    if latest.get("ram", 0) > 80:
        issues.append("RAM overload risk")
    if latest.get("disk", {}).get("usage", 0) > 90:
        issues.append("Disk nearing full capacity")
    return {"predicted_issues": issues}

def optimize_performance(snapshot):
    """
    Provide optimization suggestions based on system data
    """
    suggestions = []
    if snapshot.get("cpu", 0) > 80:
        suggestions.append("Close unused CPU-intensive apps")
    if snapshot.get("ram", 0) > 80:
        suggestions.append("Restart heavy applications")
    if snapshot.get("disk", {}).get("usage", 0) > 90:
        suggestions.append("Run disk cleanup")
    return {"suggestions": suggestions}

def generate_report(snapshot):
    """
    Generates a system report dictionary (can be passed to PDF/HTML generator)
    """
    report = {
        "CPU": snapshot.get("cpu", 0),
        "RAM": snapshot.get("ram", 0),
        "Disk Usage": snapshot.get("disk", {}).get("usage", 0),
        "Status": analyze_system(snapshot)["status"]
    }
    return report
def detect_security_threats(network_data):
    """
    Detect potential security threats from network connections
    """
    threats = []
    for conn in network_data:
        remote_addr = conn.get("remote_address", "")
        port = conn.get("remote_port")
        protocol = conn.get("protocol", "").lower()
        bytes_sent = conn.get("bytes_sent", 0)
        bytes_recv = conn.get("bytes_recv", 0)

        # normalize port to int when possible
        try:
            port_num = int(port) if port is not None else None
        except (ValueError, TypeError):
            port_num = None

        # known suspicious ports commonly used by backdoors/IRC/malware
        suspicious_ports = {4444, 5555, 6666, 6667, 31337}

        if remote_addr and port_num in suspicious_ports:
            threats.append(f"Suspicious port {port_num} on {remote_addr}")

        # treat public (non-private) addresses as potentially suspicious
        is_private = (
            remote_addr.startswith("10.")
            or remote_addr.startswith("192.168.")
            or any(remote_addr.startswith(f"172.{i}.") for i in range(16, 32))
            or remote_addr.startswith("127.")
            or remote_addr.startswith("169.254.")
        )
        if remote_addr and not is_private:
            threats.append(f"External connection to {remote_addr}:{port_num or ''}")

        # unusually high data transfer could indicate data exfiltration
        if bytes_sent > 10_000_000 or bytes_recv > 10_000_000:
            threats.append(f"High data transfer with {remote_addr}:{port_num or ''} (sent={bytes_sent}, recv={bytes_recv})")

        # check explicit connection flags
        if conn.get("status") in ("suspicious", "blocked", "failed"):
            threats.append(f"Connection {remote_addr}:{port_num or ''} reported as {conn.get('status')}")
    # return a structured result
    return {"threats": threats}
                                                  