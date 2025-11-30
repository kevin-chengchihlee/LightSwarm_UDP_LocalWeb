#v04 Kevin Lee 11/13/2025 Modified for LightSwarm Project - Data Collection

import time
import tracemalloc
import threading
import datetime
import os
import LightSwarm as LS
import statistics
import numpy as np

# Configuration
WINDOW = 30  # seconds

# Threading control
plot_stop = threading.Event()
plot_reset_flag = threading.Event()
reset_counter = 0

# Data storage
t0 = time.time()
master_count = [0, 0, 0]
current_time = 0

xs0 = np.array([])
ys0 = np.array([])

xs1 = np.array([])
ys1 = np.array([])

xs2 = np.array([])
ys2 = np.array([])

time_data = np.array([])
mem_data = np.array([])
mem_peak_data = np.array([])

# Thread-safe data access
data_lock = threading.Lock()

#tracemalloc.start()

def collect_data():
    """Background thread: collects sensor data"""
    
    global t0, xs0, ys0, xs1, ys1, xs2, ys2, current_time
    global master_count, time_data, mem_data, mem_peak_data, reset_counter
    
    device_id = 99
    value = 0

    print("[COLLECT] Data collection thread started")

    while not plot_stop.is_set():
        print("Collecting Data!!!!!!!!!!!!!!!!-//////////////////////////////////////\n")
        if plot_reset_flag.is_set():
            print("Resetting Data!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n")
            time.sleep(5)
            xs0 = np.array([])
            ys0 = np.array([])
            xs1 = np.array([])
            ys1 = np.array([])
            xs2 = np.array([])
            ys2 = np.array([])
            master_count = [0, 0, 0]
            t0 = time.time()
            current_time = 0
            
            print(f"[RESET] Counter: {reset_counter}")
            plot_reset_flag.clear()
            plot_stop.set() #<---stopping plot thread
            break
        
        try:
            device_id_, isMaster_, value_ = LS.getLSMasterBright()
            if isMaster_:
                device_id = device_id_
                value = value_
        except Exception as e:
            print(f"[ERROR] getLSMasterBright failed: {e}")
            time.sleep(0.1)
            continue
        
        current_timestamp = time.time() - t0
            
        if device_id == 0:
            if master_count[device_id] >= 30:
                master_count[0] = 0
                master_count[1] = 0
                master_count[2] = 0

            master_count[device_id] += 1
            xs0 = np.append(xs0, current_timestamp)
            ys0 = np.append(ys0, value)
            current_time = xs0[-1]
                
            if current_time > WINDOW:
                mask = xs0 >= (current_time - WINDOW)
                xs0 = xs0[mask]
                ys0 = ys0[mask]

        elif device_id == 1:
            if master_count[device_id] >= 30:
                master_count[0] = 0
                master_count[1] = 0
                master_count[2] = 0

            master_count[device_id] += 1
            xs1 = np.append(xs1, current_timestamp)
            ys1 = np.append(ys1, value)
            current_time = xs1[-1]
                
            if current_time > WINDOW:
                mask = xs1 >= (current_time - WINDOW)
                xs1 = xs1[mask]
                ys1 = ys1[mask]

        elif device_id == 2:
            if master_count[device_id] >= 30:
                master_count[0] = 0
                master_count[1] = 0
                master_count[2] = 0

            master_count[device_id] += 1
            xs2 = np.append(xs2, current_timestamp)
            ys2 = np.append(ys2, value)
            current_time = xs2[-1]
                
            if current_time > WINDOW:
                mask = xs2 >= (current_time - WINDOW)
                xs2 = xs2[mask]
                ys2 = ys2[mask]

        print("master_count = ", master_count[0], master_count[1], master_count[2])
        
        time.sleep(1)

def get_plot_data():
    """Returns current plot data (thread-safe)"""
    return {
        'time0': xs0.tolist(),
        'brightness0': ys0.tolist(),
        'time1': xs1.tolist(),
        'brightness1': ys1.tolist(),
        'time2': xs2.tolist(),
        'brightness2': ys2.tolist(),
        'master_count': master_count.copy(),
        'current_time': current_time,
        'reset_counter': reset_counter
    }

def reset_plot():
    """Reset all plot data"""
    global t0
    t0 = time.time()
    plot_reset_flag.set()

def ex_log():
    """Export data to log file"""
    global xs0, ys0, xs1, ys1, xs2, ys2, current_time, master_count, time_data

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    os.makedirs("log", exist_ok=True)
    with open(f"log/LIGHTSWARM_{timestamp}.txt", "w") as f:
        f.write("=== LightSwarm Data Log ===\n")
        f.write(f"Timestamp: {timestamp}\n\n")

        # Log master counter
        f.write("Master Count per Device:\n")
        f.write(f"Device 0: {master_count[0]}\n")
        f.write(f"Device 1: {master_count[1]}\n")
        f.write(f"Device 2: {master_count[2]}\n\n")

        # Log arrays
        f.write("=== Device 0 Data (xs0, ys0) ===\n")
        for t, v in zip(xs0, ys0):
            f.write(f"{t:.2f}, {v}\n")

        f.write("\n=== Device 1 Data (xs1, ys1) ===\n")
        for t, v in zip(xs1, ys1):
            f.write(f"{t:.2f}, {v}\n")

        f.write("\n=== Device 2 Data (xs2, ys2) ===\n")
        for t, v in zip(xs2, ys2):
            f.write(f"{t:.2f}, {v}\n")
        
    print(f"[LOG] Exported data → log/LIGHTSWARM_{timestamp}.txt")