#v04 Kevin Lee 11/13/2025 Modified for LightSwarm Project with plot

import time
import tracemalloc
import threading
import datetime
import os
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import LightSwarm as LS
import statistics

# Screen dimensions
screen_width = 1200
screen_height = 400
WINDOW = 30 #sec

plot_stop = threading.Event()
plot_reset_flag = threading.Event()

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 6))  # 2 rows, 1 column
ax1.set_facecolor('#2e2e2e')

t0 = time.time()

line0, = ax1.plot([], [], 'green', linestyle='None', marker='o', label=f"DID 0 Brightness")
line1, = ax1.plot([], [], 'yellow', linestyle='None', marker='o', label=f"DID 1 Brightness")
line2, = ax1.plot([], [], 'red', linestyle='None', marker='o', label=f"DID 2 Brightness")

xs0, ys0 = [], []
xs1, ys1 = [], []
xs2, ys2 = [], []
master_count = [0, 0, 0]

current_time = 0
time_data = []

mem_data = []
mem_peak_data = []
tracemalloc.start()

def update_plot(frame):
    pass

def plot():

    global t0, xs0, ys0, xs1, ys1, xs2, ys2, current_time, line0, line1, line2, master_count, fig
    device_id = 99
    value = 0

    ax1.set_xlabel("Time (s)")
    ax1.set_ylabel("PhotoCell Reading")
    ax1.set_title("LightSwarm Brightness")
    ax1.set_ylim(0, 5000)  # adjust based on brightness range
    ax2.set_xlabel("Device ID")
    ax2.set_ylabel("Accumulative Master Count")
    ax2.set_title("Device Master Chart")
    ani = animation.FuncAnimation(fig, update_plot, interval=1000)
    plt.show(block=False)

    while not plot_stop.is_set():
        # --- Time measurement ---
        start = time.perf_counter()
        
        if plot_reset_flag.is_set(): #reset plot
            print("Resetting Plot!!\n")
            xs0.clear(); ys0.clear()
            xs1.clear(); ys1.clear()
            xs2.clear(); ys2.clear()

            line0.set_xdata([]); line0.set_ydata([])
            line1.set_xdata([]); line1.set_ydata([])
            line2.set_xdata([]); line2.set_ydata([])

            ax1.set_xlim(0, WINDOW)

            plot_reset_flag.clear()
        
        # get brightness
        device_id_, isMaster_, value_ = LS.getLSMasterBright()
        plt.subplots_adjust(hspace=0.35)

        if(isMaster_):
            device_id = device_id_
            value = value_

        if(device_id == 0):
            if(master_count[device_id] >=30):
                master_count[0] = 0
                master_count[1] = 0
                master_count[2] = 0

            master_count[device_id] +=1
            line0.set_linewidth(2.5)
            xs0.append(time.time() - t0)
            ys0.append(value)
            line0.set_xdata(xs0)
            line0.set_ydata(ys0)
            # rolling window
            current_time = xs0[-1]

        elif(device_id == 1):
            if(master_count[device_id] >=30):
                master_count[0] = 0
                master_count[1] = 0
                master_count[2] = 0

            master_count[device_id] +=1
            line1.set_linewidth(2.5)
            xs1.append(time.time() - t0)
            ys1.append(value)
            line1.set_xdata(xs1)
            line1.set_ydata(ys1)
            current_time = xs1[-1]

        elif(device_id == 2):
            if( master_count[device_id]>=30):
                master_count[0] = 0
                master_count[1] = 0
                master_count[2] = 0

            master_count[device_id] +=1
            line2.set_linewidth(2.5)
            xs2.append(time.time() - t0)
            ys2.append(value)
            line2.set_xdata(xs2)
            line2.set_ydata(ys2)
            current_time = xs2[-1]

        print("master_count[device_id] = ", master_count[0], master_count[1], master_count[2])

        if current_time > WINDOW:
            ax1.set_xlim(current_time - WINDOW, current_time)
        else:
            ax1.set_xlim(0, WINDOW)

        # Update bar chart
        ax2.clear()
        ax2.set_xticks([0, 1, 2])
        ax2.set_xticklabels(["Device 0", "Device 1", "Device 2"])
        ax2.set_ylim(0, 30)
        ax2.bar(
            [0,1,2],
            [master_count[0], master_count[1], master_count[2]],
            color=["green", "yellow", "red"],
            width=0.5
        )
        # --- Time measurement ---
        end = time.perf_counter()
        exe_time = end-start
        time_data.append(exe_time)
        
        print(f"Time: {end - start:.6f}s")
        
        # --- Memory measurement ---
        cur_mem, peak_mem = tracemalloc.get_traced_memory()
        mem_data.append(cur_mem)
        mem_peak_data.append(peak_mem)
        print(f"MEM: {cur_mem/1024:.2f} KB, PEAK: {peak_mem/1024:.2f} KB")
        
        plt.pause(1)

def reset_plot():

    global t0, master_count

    master_count = [0, 0, 0]
    t0   = time.time()
    plot_reset_flag.set()

def ex_log():
    global xs0, ys0, xs1, ys1, xs2, ys2, current_time, master_count, time_data

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    os.makedirs("log", exist_ok=True)
    with open(f"log/LIST_{timestamp}.txt", "w") as f:
        f.write("=== LightSwarm Data Log ===\n")
        f.write(f"Timestamp: {timestamp}\n\n")

        #Log master counter
        f.write("Master Count per Device:\n")
        f.write(f"Device 0: {master_count[0]}\n")
        f.write(f"Device 1: {master_count[1]}\n")
        f.write(f"Device 2: {master_count[2]}\n\n")

        #Log arrays
        f.write("=== Device 0 Data (xs0, ys0) ===\n")
        for t, v in zip(xs0, ys0):
            f.write(f"{t:.2f}, {v}\n")

        f.write("\n=== Device 1 Data (xs1, ys1) ===\n")
        for t, v in zip(xs1, ys1):
            f.write(f"{t:.2f}, {v}\n")

        f.write("\n=== Device 2 Data (xs2, ys2) ===\n")
        for t, v in zip(xs2, ys2):
            f.write(f"{t:.2f}, {v}\n")
        
        f.write("\n=== plot execution time sec ===\n")
        for t in time_data:
            f.write(f"{t:.6f}\n")
            
        f.write("\n=== plot AVG execution time sec ===\n")
        avg_time = statistics.mean(time_data)
        f.write(f"{avg_time:.6f}\n")
        print(f"Average execution time: {avg_time:.6f}s")
        
        f.write("\n=== Memory Usage (KB) ===\n")
        for m in mem_data:
            f.write(f"{m/1024:.2f}\n")
            
        f.write("\n=== AVG Memory Usage (KB) ===\n")
        avg_mem = statistics.mean(mem_data)
        f.write(f"{avg_mem/1024:.2f}\n")
        
        f.write("\n=== Peak Memory (KB) ===\n")
        for m in mem_peak_data:
            f.write(f"{m/1024:.2f}\n")
        
    print(f"[LOG] Exported data → {timestamp}.txt")
