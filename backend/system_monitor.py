import psutil
import time
from backend.database import log_system_snapshot

def run_monitor():
    """Continuously read system stats and log to MongoDB."""
    while True:
        cpu = psutil.cpu_percent(interval=1)
        ram = psutil.virtual_memory().percent
        disk = {
            'usage': psutil.disk_usage("/").percent,
            'health': {}  # optional placeholder for health per partition
        }
        net_io = psutil.net_io_counters(pernic=True)
        network = [{'interface': k, 'bytes_sent': v.bytes_sent, 'bytes_recv': v.bytes_recv} for k,v in net_io.items()]
        processes = [p.info for p in psutil.process_iter(['pid','name','cpu_percent','memory_percent'])]
        
        log_system_snapshot(cpu, ram, disk, network, processes)
        time.sleep(2)  # log every 2 seconds

if __name__ == "__main__":
    run_monitor()
