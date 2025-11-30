import spidev
import time
import random
import LightSwarm as LS

MAT_VAL = [0x00, 0x80, 0xC0, 0xE0, 0xF0, 0xF8, 0xFC, 0xFE, 0xFF]
DATA = [0, 0, 0, 0, 0, 0, 0, 0, 0]
raw_value = 0

class LED_MAT:
    def __init__(self, name):
        # Constructor (runs when object is created)
        self.name = name
        self.status = False

    def spi_init(self, bus, device, max_spd, mode):

        self.spi = spidev.SpiDev()
        self.spi.open(bus, device)  # bus 0, device 0 (spidev0.0)
        self.spi.max_speed_hz = max_spd  # 1 MHz
        self.spi.mode = mode
        self.status = True

    def mat_init(self):
        # MAX7219 init
        self.show(0x09, 0x00)  # no decode
        self.show(0x0A, 0x08)  # brightness (0x00–0x0F)
        self.show(0x0B, 0x07)  # scan all 8 rows
        self.show(0x0C, 0x01)  # exit shutdown mode
        self.show(0x0F, 0x00)  # display test off

        for row in range(1, 9):
            self.show(row, 0x00)
        time.sleep(0.5)

    def data_queue(self, data):
        DATA[8] = DATA[7]
        DATA[7] = DATA[6]
        DATA[6] = DATA[5]
        DATA[5] = DATA[4]
        DATA[4] = DATA[3]
        DATA[3] = DATA[2]
        DATA[2] = DATA[1]
        DATA[1] = DATA[0]
        DATA[0] = data

    def show(self, reg, data):
        if self.status is True:
            self.spi.xfer2([reg, data])
        else:
            print("LED Matrix Not Yet Init YO~~")

    def close(self):
        self.spi.xfer2([0x0C, 0x00])

    def show_swarm(self):
        global raw_value

        while True:
            device_id_, isMaster_, value_ = LS.getLSMasterBright()
            if(isMaster_):
                device_id = device_id_
                raw_value = value_
                raw_value /= 511 #to 0 - 8
            
            if raw_value > 8:
                raw_value = 8
            if raw_value < 0:
                raw_value = 0
            raw_value = int(raw_value)
            value = MAT_VAL[raw_value] #get hex 
            self.data_queue(value) #push data to DATA[]
            for i in range (0, 8):
                self.show(i+1, DATA[i])

            time.sleep(1)
