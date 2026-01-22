#!/usr/bin/python

from PCF8574 import PCF8574;


# ============================================================================
# Raspi PCF8574 8-Channel GPIO
# ============================================================================

class BUSofPCF8574:

    def __init__(self, address=0x21, debug=False):
        self.devices = [PCF8574(0x21), PCF8574(0x20)]

    def click(self, channel):
        device = self.devices[channel // 8]
        device.click(channel % 8)


if __name__ == '__main__':
    pc = BUSofPCF8574()
    pc.click(8)
    # for i in range(16):
    #       pc.click(i)
