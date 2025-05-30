#!/usr/bin/python

import time
import serial


class Arduino:
    def __init__(self, port='/dev/ttyUSB0', baudrate=9600, timeout=0.1):
        self.arduino = serial.Serial(port=port, baudrate=baudrate, timeout=timeout)
        self.values = ['-','+','1','2','3','4','5','6','7','8','9','A','B','C','D','E','F']

    def write(self, index):
        value = self.values[index]
        print(value)
        self.arduino.write(value.encode('utf-8'))

    def click(self, hex_str):
        try:
            index = int(hex_str, 16) if isinstance(hex_str, str) else int(hex_str)
            print(index)
            self.write(index)
            time.sleep(0.05)
            self.arduino.write(b'p')
        except (ValueError, IndexError) as e:
            print(f"[Arduino] Invalid input '{hex_str}': {e}")
