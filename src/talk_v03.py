#Kevin Lee 10/11/2025
#v03 Kevin Lee 11/03/2025 Modified for LightSwarm Project
import time
import threading
import UDP_v03 as UDP
import state_machine_v04 as STATE
import LightSwarm as LS
import plot as PLOT
import led_matrix as MAT
import web as WEB

if __name__=='__main__':
    
    STATE.gpio_setup()
    #init a led matrix
    mat = MAT.LED_MAT("RPi LED Mat")
    mat.spi_init(0, 0, 1000000, 0)
    time.sleep(0.2)
    mat.mat_init()
    time.sleep(0.2)

    receiver_thread = threading.Thread(target=UDP.UDP_Receive, daemon=True)
    receiver_thread.start()# Put UDP listening to thread to ensuring listening
    processPacket_thread = threading.Thread(target=LS.processPacket, daemon=True)
    processPacket_thread.start()
    ledMatrix_thread = threading.Thread(target=mat.show_swarm, daemon=True)
    ledMatrix_thread.start()

    #plot_thread = threading.Thread(target=PLOT.collect_data, daemon=True)
    #plot_thread.start()

    print("####################################################")
    print("System Up! Listening to LightSwarm Packets!!")
    print("####################################################")
    
    print("=" * 60)
    print("🚀 Starting LightSwarm Web Dashboard (Real-Time Plotting)")
    print("=" * 60)
    
    print("\n📊 Dashboard URLs:")
    print("   Local:   http://localhost:5000")
    print("   Network: http://<raspberry-pi-ip>:5000")
    print("\n💡 Press Ctrl+C to stop")
    print("=" * 60)

    try:
        while True:
            if STATE.get_plot_enb():
                PLOT.collect_data()
        
    except KeyboardInterrupt:
        PLOT.plot_stop.set()
        time.sleep(0.1)
        mat.close()
        print("Exiting...")

    try:
        WEB.web.run(host="0.0.0.0", port=5000, debug=False, threaded=True)

    except:
        print("Web fail to init...")
