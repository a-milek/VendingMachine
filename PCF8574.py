#!/usr/bin/python

import time
import math

from smbus2 import SMBus, i2c_msg


# ============================================================================
# Raspi PCF8574 8-Channel GPIO
# ============================================================================

class PCF8574:

    def __init__(self, address=0x21, debug=False):
        self.bus = SMBus(1)
        self.address = address
        self.debug = debug
        self.current_msg = 0b0


        if (self.debug):
            print("Reseting PCF8574")

    def set_channel(self, channel, value):
        if value:
            self.current_msg |= (1 << channel)
        else:
            self.current_msg &= ~(1 << channel)
        if (self.debug):        
            print(bin(self.current_msg))
        self.bus.write_byte(self.address, ~self.current_msg)

    def click(self, channel):
        self.set_channel(channel, 1)
        time.sleep(2)
        self.set_channel(channel, 0)


if __name__ == '__main__':
    pc = PCF8574(0x20)
    pc.click(1)
    for i in range(8):
        pc.click(i)
