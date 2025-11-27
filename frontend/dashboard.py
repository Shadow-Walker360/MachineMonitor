import sys
import threading
import time
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QMessageBox
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import Qt
from frontend.cards import create_card
from backend.database import db
import plotly.graph_objs as go
from plotly.offline import plot

# MongoDB collections
logs_collection = db["system_logs"]
ai_collection = db["ai_analysis"]

# Global variables for live data
latest_snapshot = {}
latest_ai = {}
history = {
    "cpu": [], "ram": [], "disk": [],
    "network_sent": [], "network_recv": []
}

# Thresholds for alerts
thresholds = {
    "cpu": 85,
    "ram": 90,
    "disk": 90,
    "network": 10000000  # bytes/sec, example
}

# -------------------------- Data Fetch Thread --------------------------
def fetch_latest_data():
    global latest_snapshot, latest_ai, history
    while True:
        snapshot = logs_collection.find_one(sort=[("timestamp", -1)])
        ai_data = ai_collection.find_one(sort=[("timestamp", -1)])
        if snapshot:
            latest_snapshot = snapshot
            history["cpu"].append(snapshot.get("cpu", 0))
            history["ram"].append(snapshot.get("ram", 0))
            history["disk"].append(snapshot.get("disk", {}).get("usage", 0))
            net = snapshot.get("network", [])
            bytes_sent = sum(c.get("bytes_sent",0) for c in net) if net else 0
            bytes_recv = sum(c.get("bytes_recv",0) for c in net) if net else 0
            history["network_sent"].append(bytes_sent)
            history["network_recv"].append(bytes_recv)

            # Limit history
            max_points = 50
            for key in history:
                if len(history[key]) > max_points:
                    history[key] = history[key][-max_points:]
        if ai_data:
            latest_ai = ai_data
        time.sleep(2)

# -------------------------- Plotly Chart Creator --------------------------
def create_chart(title, y_data, y_label):
    fig = go.Figure()
    fig.add_trace(go.Scatter(y=y_data, mode='lines+markers', name=title))
    fig.update_layout(title=title, yaxis_title=y_label, margin=dict(l=20,r=20,t=30,b=20))
    return plot(fig, output_type='div', include_plotlyjs='cdn', auto_open=False)

# -------------------------- Dashboard --------------------------
def start_dashboard():
    app = QApplication(sys.argv)
    window = QWidget()
    window.setWindowTitle("Machine Monitor Dashboard")
    window.setGeometry(100, 100, 1300, 750)
    main_layout = QVBoxLayout()

    # ----------------- Top Cards -----------------
    card_layout = QHBoxLayout()
    cpu_card, cpu_label = create_card("CPU Usage", show_cpu_details)
    ram_card, ram_label = create_card("RAM Usage", show_ram_details)
    disk_card, disk_label = create_card("Disk Usage", show_disk_details)
    net_card, net_label = create_card("Network Activity", show_network_details)
    ai_card, ai_label = create_card("AI Insights", show_ai_details)
    card_layout.addWidget(cpu_card)
    card_layout.addWidget(ram_card)
    card_layout.addWidget(disk_card)
    card_layout.addWidget(net_card)
    card_layout.addWidget(ai_card)
    main_layout.addLayout(card_layout)

    # ----------------- Charts -----------------
    chart_layout = QHBoxLayout()
    cpu_chart_view = QWebEngineView()
    ram_chart_view = QWebEngineView()
    disk_chart_view = QWebEngineView()
    net_chart_view = QWebEngineView()
    chart_layout.addWidget(cpu_chart_view)
    chart_layout.addWidget(ram_chart_view)
    chart_layout.addWidget(disk_chart_view)
    chart_layout.addWidget(net_chart_view)
    main_layout.addLayout(chart_layout)

    window.setLayout(main_layout)

    # ----------------- Threads -----------------
    threading.Thread(target=fetch_latest_data, daemon=True).start()
    threading.Thread(target=lambda: update_ui(cpu_label, ram_label, disk_label, net_label,
                                               cpu_chart_view, ram_chart_view, disk_chart_view, net_chart_view), daemon=True).start()

    window.show()
    sys.exit(app.exec_())

# -------------------------- UI Update --------------------------
def update_ui(cpu_label, ram_label, disk_label, net_label, cpu_chart_view, ram_chart_view, disk_chart_view, net_chart_view):
    global latest_snapshot, latest_ai
    while True:
        # Update cards
        cpu_val = latest_snapshot.get("cpu", "N/A")
        ram_val = latest_snapshot.get("ram", "N/A")
        disk_val = latest_snapshot.get("disk", {}).get("usage", "N/A")
        net_val = len(latest_snapshot.get("network", []))
        cpu_label.setText(f"{cpu_val}%")
        ram_label.setText(f"{ram_val}%")
        disk_label.setText(f"{disk_val}%")
        net_label.setText(f"{net_val} connections")

        # Color alerts
        cpu_label.setStyleSheet(f"color: {'red' if cpu_val >= thresholds['cpu'] else 'green'}")
        ram_label.setStyleSheet(f"color: {'red' if ram_val >= thresholds['ram'] else 'green'}")
        disk_label.setStyleSheet(f"color: {'red' if disk_val >= thresholds['disk'] else 'green'}")
        net_label.setStyleSheet(f"color: {'red' if net_val >= 100 else 'green'}")

        # Update charts
        cpu_chart_view.setHtml(create_chart("CPU Usage", history["cpu"], "CPU %"))
        ram_chart_view.setHtml(create_chart("RAM Usage", history["ram"], "RAM %"))
        disk_chart_view.setHtml(create_chart("Disk Usage", history["disk"], "Disk %"))
        net_chart_view.setHtml(create_chart("Network Sent", history["network_sent"], "Bytes"))

        time.sleep(3)

# -------------------------- Card Click Handlers --------------------------
def show_cpu_details():
    cpu = latest_snapshot.get("cpu", "N/A")
    processes = latest_snapshot.get("processes", [])
    msg = f"CPU Usage: {cpu}%\nTop 5 Processes:\n"
    for p in sorted(processes, key=lambda x: x.get("cpu_percent",0), reverse=True)[:5]:
        msg += f"{p['name']} (PID {p['pid']}): {p['cpu_percent']}%\n"
    QMessageBox.information(None, "CPU Details", msg)

def show_ram_details():
    ram = latest_snapshot.get("ram", "N/A")
    processes = latest_snapshot.get("processes", [])
    msg = f"RAM Usage: {ram}%\nTop 5 Memory Processes:\n"
    for p in sorted(processes, key=lambda x: x.get("memory_percent",0), reverse=True)[:5]:
        msg += f"{p['name']} (PID {p['pid']}): {p['memory_percent']:.2f}%\n"
    QMessageBox.information(None, "RAM Details", msg)

def show_disk_details():
    disk = latest_snapshot.get("disk", {})
    usage = disk.get("usage", "N/A")
    health = disk.get("health", {})
    msg = f"Disk Usage: {usage}%\nPartition Health:\n"
    for part, status in health.items():
        msg += f"{part}: {status}\n"
    QMessageBox.information(None, "Disk Details", msg)

def show_network_details():
    network = latest_snapshot.get("network", [])
    msg = f"Active Connections: {len(network)}\n"
    for conn in network[:5]:
        local = conn.get("local_address")
        remote = conn.get("remote_address")
        status = conn.get("status")
        msg += f"{local} → {remote} ({status})\n"
    QMessageBox.information(None, "Network Details", msg)

def show_ai_details():
    if not latest_ai:
        QMessageBox.information(None, "AI Insights", "No AI data available yet.")
        return
    analysis = latest_ai.get("analysis", {}).get("status", "N/A")
    recommendations = latest_ai.get("optimizations", {}).get("suggestions", [])
    report = latest_ai.get("report", {}).get("report", "N/A")
    msg = f"AI Status: {analysis}\nRecommendations:\n"
    for r in recommendations:
        msg += f"- {r}\n"
    msg += f"\nReport:\n{report}"
    QMessageBox.information(None, "AI Insights", msg)

# -------------------------- Entry Point --------------------------
if __name__ == "__main__":
    start_dashboard()
