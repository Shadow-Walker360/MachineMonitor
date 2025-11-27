from pymongo import MongoClient
from datetime import datetime

# MongoDB setup
MONGO_URI = "mongodb://localhost:27017"
DB_NAME = "machine_monitor"

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

# Collections
logs_collection = db["system_logs"]
ai_collection = db["ai_analysis"]

def log_system_snapshot(cpu, ram, disk, network, processes):
    doc = {
        "timestamp": datetime.utcnow(),
        "cpu": cpu,
        "ram": ram,
        "disk": disk,
        "network": network,
        "processes": processes
    }
    logs_collection.insert_one(doc)

def log_ai_analysis(analysis, predictions, optimizations, threats, report):
    doc = {
        "timestamp": datetime.utcnow(),
        "analysis": analysis,
        "predictions": predictions,
        "optimizations": optimizations,
        "threats": threats,
        "report": report
    }
    ai_collection.insert_one(doc)

if __name__ == "__main__":
    print("MongoDB setup complete.")
