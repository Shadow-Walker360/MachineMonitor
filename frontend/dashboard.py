# frontend/dashboard.py
import sys
import threading
import time
from PyQt5.QtWidgets import QApplication, QVBoxLayout, QHBoxLayout, QLabel, QMessageBox, QMainWindow, QWidget
from PyQt5.QtWebEngineWidgets import QWebEngineView
from .cards import create_card
from backend.database import db
import plotly.graph_objs as go
from plotly.offline import plot

# MongoDB collections
logs_collection = db["system_logs"]
ai_collection = db["ai_analysis"]

# Global variables for live data
latest_snapshot = {}
latest_ai = {}
history = {"cpu": [], "ram": [], "disk": [], "network_sent": [], "network_recv": []}

# Thresholds for alerts
thresholds = {"cpu": 85, "ram": 90, "disk": 90, "network": 10000000}

class dashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Machine Monitor Dashboard")
        self.setGeometry(100, 100, 1300, 750)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.main_layout = QVBoxLayout()
        central_widget.setLayout(self.main_layout)

        # ----------------- Top Cards -----------------
        self.card_layout = QHBoxLayout()
        self.cpu_card, self.cpu_label = create_card("CPU Usage", self.show_cpu_details)
        self.ram_card, self.ram_label = create_card("RAM Usage", self.show_ram_details)
        self.disk_card, self.disk_label = create_card("Disk Usage", self.show_disk_details)
        self.net_card, self.net_label = create_card("Network Activity", self.show_network_details)
        self.ai_card, self.ai_label = create_card("AI Insights", self.show_ai_details)
        for card in [self.cpu_card, self.ram_card, self.disk_card, self.net_card, self.ai_card]:
            self.card_layout.addWidget(card)
        self.main_layout.addLayout(self.card_layout)

        # ----------------- Charts -----------------
        self.chart_layout = QHBoxLayout()
        self.cpu_chart_view = QWebEngineView()
        self.ram_chart_view = QWebEngineView()
        self.disk_chart_view = QWebEngineView()
        self.net_chart_view = QWebEngineView()
        for chart in [self.cpu_chart_view, self.ram_chart_view, self.disk_chart_view, self.net_chart_view]:
            self.chart_layout.addWidget(chart)
        self.main_layout.addLayout(self.chart_layout)

        # ----------------- Start Threads -----------------
        threading.Thread(target=self.fetch_latest_data, daemon=True).start()
        threading.Thread(target=self.update_ui, daemon=True).start()

    # -------------------------- Data Fetch --------------------------
    def fetch_latest_data(self):
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
                history["network_sent"].append(sum(c.get("bytes_sent", 0) for c in net))
                history["network_recv"].append(sum(c.get("bytes_recv", 0) for c in net))
                for key in history:
                    if len(history[key]) > 50:
                        history[key] = history[key][-50:]
            if ai_data:
                latest_ai = ai_data
            time.sleep(2)

    # -------------------------- Chart Helper --------------------------
    def create_chart(self, title, y_data, y_label):
        fig = go.Figure()
        fig.add_trace(go.Scatter(y=y_data, mode='lines+markers', name=title))
        fig.update_layout(title=title, yaxis_title=y_label, margin=dict(l=20,r=20,t=30,b=20))
        return plot(fig, output_type='div', include_plotlyjs='cdn', auto_open=False)

    # -------------------------- UI Update --------------------------
    def update_ui(self):
        global latest_snapshot
        while True:
            cpu_val = latest_snapshot.get("cpu", 0)
            ram_val = latest_snapshot.get("ram", 0)
            disk_val = latest_snapshot.get("disk", {}).get("usage", 0)
            net_val = len(latest_snapshot.get("network", []))
            self.cpu_label.setText(f"{cpu_val}%")
            self.ram_label.setText(f"{ram_val}%")
            self.disk_label.setText(f"{disk_val}%")
            self.net_label.setText(f"{net_val} connections")

            # Color thresholds
            self.cpu_label.setStyleSheet(f"color: {'red' if cpu_val >= thresholds['cpu'] else 'green'}")
            self.ram_label.setStyleSheet(f"color: {'red' if ram_val >= thresholds['ram'] else 'green'}")
            self.disk_label.setStyleSheet(f"color: {'red' if disk_val >= thresholds['disk'] else 'green'}")
            self.net_label.setStyleSheet(f"color: {'red' if net_val >= 100 else 'green'}")

            # Update charts
            self.cpu_chart_view.setHtml(self.create_chart("CPU Usage", history["cpu"], "CPU %"))
            self.ram_chart_view.setHtml(self.create_chart("RAM Usage", history["ram"], "RAM %"))
            self.disk_chart_view.setHtml(self.create_chart("Disk Usage", history["disk"], "Disk %"))
            self.net_chart_view.setHtml(self.create_chart("Network Sent", history["network_sent"], "Bytes"))

            time.sleep(3)

    # -------------------------- Card Handlers --------------------------
    def show_cpu_details(self):
        cpu = latest_snapshot.get("cpu", "N/A")
        processes = latest_snapshot.get("processes", [])
        msg = f"CPU Usage: {cpu}%\nTop 5 Processes:\n"
        for p in sorted(processes, key=lambda x: x.get("cpu_percent",0), reverse=True)[:5]:
            msg += f"{p['name']} (PID {p['pid']}): {p['cpu_percent']}%\n"
        QMessageBox.information(self, "CPU Details", msg)

    def show_ram_details(self):
        ram = latest_snapshot.get("ram", "N/A")
        processes = latest_snapshot.get("processes", [])
        msg = f"RAM Usage: {ram}%\nTop 5 Memory Processes:\n"
        for p in sorted(processes, key=lambda x: x.get("memory_percent",0), reverse=True)[:5]:
            msg += f"{p['name']} (PID {p['pid']}): {p['memory_percent']:.2f}%\n"
        QMessageBox.information(self, "RAM Details", msg)

    def show_disk_details(self):
        disk = latest_snapshot.get("disk", {})
        usage = disk.get("usage", "N/A")
        health = disk.get("health", {})
        msg = f"Disk Usage: {usage}%\nPartition Health:\n"
        for part, status in health.items():
            msg += f"{part}: {status}\n"
        QMessageBox.information(self, "Disk Details", msg)

    def show_network_details(self):
        network = latest_snapshot.get("network", [])
        msg = f"Active Connections: {len(network)}\n"
        for conn in network[:5]:
            local = conn.get("local_address")
            remote = conn.get("remote_address")
            status = conn.get("status")
            msg += f"{local} → {remote} ({status})\n"
        QMessageBox.information(self, "Network Details", msg)

    def show_ai_details(self):
        if not latest_ai:
            QMessageBox.information(self, "AI Insights", "No AI data available yet.")
            return
        analysis = latest_ai.get("analysis", {}).get("status", "N/A")
        recommendations = latest_ai.get("optimizations", {}).get("suggestions", [])
        report = latest_ai.get("report", {}).get("report", "N/A")
        msg = f"AI Status: {analysis}\nRecommendations:\n"
        for r in recommendations:
            msg += f"- {r}\n"
        msg += f"\nReport:\n{report}"
        QMessageBox.information(self, "AI Insights", msg)


# -------------------------- Entry Point --------------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    dashboard = dashboard()
    dashboard.show()
    sys.exit(app.exec_())
