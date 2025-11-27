# MachineMonitor

**MachineMonitor** is a professional offline-capable desktop system monitoring and analytics tool built in Python. It provides **real-time system metrics, AI-based insights, and interactive dashboards** for CPU, RAM, Disk, Network, and running processes. The application integrates with **MongoDB** to store historical data, enabling predictive analytics and performance optimization suggestions.

---

## **Features**

### 1. **Live System Monitoring**
- Tracks CPU, RAM, Disk, and Network usage in real time.
- Monitors active processes and top resource consumers.
- Tracks disk partitions and health status.
- Detects potential system anomalies.

### 2. **AI Analysis & Optimization**
- Predicts potential system issues based on historical data.
- Provides optimization recommendations (close heavy apps, clear temp files, etc.).
- Generates detailed system reports automatically.

### 3. **Interactive Dashboard**
- Built with **PyQt5** and **Plotly** for dynamic charts.
- Color-coded cards to indicate critical thresholds (CPU/RAM/Disk/Network).
- Clickable cards to view detailed system metrics and AI insights.
- Live charts for CPU, RAM, Disk usage, and Network traffic.
- Fully offline-capable and visually intuitive.

### 4. **Backend & Database**
- Uses **MongoDB** to store system snapshots and AI analysis.
- Multi-threaded architecture for continuous monitoring.
- Easy to extend with additional modules like network scanning or custom alerts.

---

## **Installation**

1. Clone the repository:

```bash
git clone https://github.com/Shadow-Walker360/MachineMonitor.git
cd MachineMonitor
