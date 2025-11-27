def analyze_system(data):
    """
    Analyze CPU, RAM, Disk, Network usage and detect anomalies
    """
    cpu = data.get("cpu", 0)
    ram = data.get("ram", 0)
    disk = data.get("disk", {}).get("usage", 0)
    status = "Normal"
    if cpu > 85 or ram > 90 or disk > 90:
        status = "Warning"
    return {"status": status, "recommendation": "Monitor resources closely"}

def predict_issues(history):
    """
    Predict potential issues based on historical data
    """
    # Placeholder for ML model integration
    return {"predicted_issues": []}

def optimize_performance(data):
    """
    Suggestions to improve system performance
    """
    suggestions = []
    if data.get("cpu",0) > 80:
        suggestions.append("Close heavy applications")
    if data.get("ram",0) > 85:
        suggestions.append("Free up memory or restart unused apps")
    if data.get("disk", {}).get("usage",0) > 85:
        suggestions.append("Clean temporary files or expand storage")
    return {"suggestions": suggestions}

def generate_report(data):
    """
    Generate a system report
    """
    return {"report": "System is running normally" if data.get("cpu",0)<85 else "System under load"}
