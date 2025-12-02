#Kevin Lee 10/11/2025
#Kevin Lee 10/20/2025 LED bug fix
#Kevin Lee 10/24/2025 Error mode recovery bug fix
#v03 Kevin Lee 11/03/2025 Modified for LightSwarm Project
#v04 Kevin Lee 11/13/2025 Modified for LightSwarm Project with plot
#v05 Kevin Lee 11/29/2025 Modified for CodeRED

import RPi.GPIO as GPIO
import time
import UDP_v03 as UDP
import LightSwarm as LS
import plot as PLOT
import threading
import re
import web as WEB

# Pin definitions (BOARD numbering)
led_r = 37   # Red LED
led_y = 33   # Yellow LED
led_g = 31   # Green LED
led_w = 29   # White LED
btn   = 36   # Push button

led_state = False
sys_state = 0 #0 init #1 operation #2 plot #3 reset
new_msg_cnt = 0
pre_msg_cnt = 0
non_msg_cnt = 0
led_ind = 0
bright_value = 0
plot_enb = False

blink_stop     = threading.Event() #for stop led blink
blink_rgy_stop = threading.Event() #for stop led rgy blink
photosns_stop  = threading.Event() #for stop photo sense

def button_callback(channel):
    state_machine()

def state_machine():
    global sys_state
    
    if sys_state == 0: #from init to operation
        m_operation()

    elif sys_state == 1:  #from norm to reset #not used
        #photosns_stop.set()
        #blink_rgy_stop.set()
        m_reset() #to reset
        m_operation()

    elif sys_state == 2: #Reset swarm and plot
        photosns_stop.set()
        blink_rgy_stop.set()
        m_reset() #reset swarm
        m_operation()

def photo_sns():
    global new_msg_cnt
    global pre_msg_cnt
    global led_ind
    global bright_value
    value = 0
    print("################")
    print("In photo sns now")
    print("################")
    
    while not photosns_stop.is_set(): #sys_state==1 and 
        pre_msg_cnt = new_msg_cnt
        device_id, isMaster, value = LS.getLSMasterBright()
        #print("photo_sns Receiving Packet. device_id, isMaster, value = ",device_id,', ',isMaster,', ',value, '\n')
        new_msg_cnt = UDP.get_new_msg_cnt()
        
        if(isMaster):
            blink_rgy_stop.clear()
            bright_value = value
            print("bright_value = ",bright_value, ", value= ", value)
            if device_id == 0:
                led_ind = led_g
                #print("LED indicator is:", led_g, '\n')
                GPIO.output(led_r, GPIO.LOW)
                GPIO.output(led_y, GPIO.LOW)
            elif device_id == 1:
                led_ind = led_y
                #print("LED indicator is:", led_y, '\n')
                GPIO.output(led_r, GPIO.LOW)
                GPIO.output(led_g, GPIO.LOW)
            elif device_id == 2:
                led_ind = led_r
                #print("LED indicator is:", led_r, '\n')
                GPIO.output(led_y, GPIO.LOW)
                GPIO.output(led_g, GPIO.LOW)
            
        time.sleep(0.2)

def blink_rgy_led():
    global led_ind
    global bright_value
    while not blink_rgy_stop.is_set():

        if led_ind > 0:
            if (bright_value>0 and bright_value<1000):
                GPIO.output(led_ind, not GPIO.input(led_ind))
                time.sleep(0.5)
            elif (bright_value>=1000 and bright_value<2000):
                GPIO.output(led_ind, not GPIO.input(led_ind))
                time.sleep(0.3)
            elif (bright_value>=2000 and bright_value<3000):
                GPIO.output(led_ind, not GPIO.input(led_ind))
                time.sleep(0.2)
            elif (bright_value>=3000):
                GPIO.output(led_ind, not GPIO.input(led_ind))
                time.sleep(0.1)
        
def m_operation():
    global sys_state
    global message_r
    
    sys_state = 1
    GPIO.output(led_w, GPIO.HIGH)
    print("#################")
    print("In operation mode")
    print("#################")

    photosns_stop.clear() #clear the stop event
    photosns_thread = threading.Thread(target=photo_sns, daemon=True)
    photosns_thread.start()
    
    blink_rgy_stop.clear() #clear the stop event
    blink_RGY_thread = threading.Thread(target=blink_rgy_led, daemon=True)
    blink_RGY_thread.start()

    m_plot() #to plot state

    time.sleep(0.2)

def m_plot():
    global sys_state
    global message_r
    global plot_enb
    
    sys_state = 2
    plot_enb = True

    PLOT.plot_stop.clear()
    plot_thread = threading.Thread(target=PLOT.collect_data, daemon=True)
    plot_thread.start()

    print("##################")
    print("Plot")
    print("##################")

def m_reset():
    global sys_state, plot_enb
    
    sys_state = 3

    UDP.setLSCommand("RESETSWARM")#setting LS cmd to UDP layer
    print("##################")
    print("Reset Swarm")
    print("##################")
    plot_enb = False
    PLOT.ex_log() #<---log data
    PLOT.reset_plot() #<---resetting plot time and data
    
    GPIO.output(led_y, GPIO.HIGH)
    GPIO.output(led_w, GPIO.HIGH)
    GPIO.output(led_r, GPIO.LOW)
    GPIO.output(led_w, GPIO.LOW)
    GPIO.output(led_g, GPIO.LOW)
    time.sleep(3)
    GPIO.output(led_y, GPIO.LOW)

def gpio_setup():
    # GPIO setup
    GPIO.setmode(GPIO.BOARD)  # use BOARD numbering, not physical pins
    GPIO.setwarnings(False)
    
    # Set LEDs as outputs
    GPIO.setup(led_r, GPIO.OUT)
    GPIO.setup(led_y, GPIO.OUT)
    GPIO.setup(led_g, GPIO.OUT)
    GPIO.setup(led_w, GPIO.OUT)
    #Blink LEDs
    GPIO.output(led_r, GPIO.LOW)
    GPIO.output(led_y, GPIO.LOW)
    GPIO.output(led_g, GPIO.LOW)
    GPIO.output(led_w, GPIO.LOW)
    time.sleep(0.5)
    GPIO.output(led_r, GPIO.HIGH)
    GPIO.output(led_y, GPIO.HIGH)
    GPIO.output(led_g, GPIO.HIGH)
    GPIO.output(led_w, GPIO.HIGH)
    time.sleep(0.5)
    GPIO.output(led_r, GPIO.LOW)
    GPIO.output(led_y, GPIO.LOW)
    GPIO.output(led_g, GPIO.LOW)
    GPIO.output(led_w, GPIO.LOW)
    
    # Set button as input with pull-down resistor
    GPIO.setup(btn, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    # Add interrupt to the push btn
    GPIO.add_event_detect(btn, GPIO.RISING, callback=button_callback, bouncetime=300)

def get_plot_enb():

    return plot_enb