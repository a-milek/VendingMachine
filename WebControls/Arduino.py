#!/usr/bin/python

import time
import serial


class Arduino:
    def __init__(self, port='/dev/serial/by-path/platform-xhci-hcd.1-usb-0:2:1.0-port0', baudrate=9600, timeout=0.1):
        self.arduino = serial.Serial(port=port, baudrate=baudrate, timeout=timeout)
        self.values = ['-','+','1','2','3','4','5','6','7','8','9','A','B','C','D','E','F','G','H']
        self.char_to_index = {v: i for i, v in enumerate(self.values)}  # <--- DODAJ TO

    def write(self, index):
        value = self.values[index]
        print(value)
        self.arduino.write(value.encode('utf-8'))

    def click(self, key):
        try:
            if isinstance(key, int):
                index = key
            elif isinstance(key, str):
                key = key.upper()
                if key in self.char_to_index:
                    index = self.char_to_index[key]
                elif key.isdigit() or (len(key) == 1 and key in "ABCDEF"):
                    index = int(key, 16)
                else:
                    raise ValueError(f"Invalid key '{key}'")
            else:
                raise ValueError(f"Unsupported type: {type(key)}")

            self.write(index)
            time.sleep(0.05)
            self.arduino.write(b'p')

        except (ValueError, IndexError) as e:
            print(f"[Arduino] Invalid input '{key}': {e}")

