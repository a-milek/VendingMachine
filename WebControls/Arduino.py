#!/usr/bin/python

import time
import serial


class Arduino:
    def __init__(self, port='/dev/serial/by-path/platform-xhci-hcd.1-usb-0:2:1.0-port0', baudrate=9600, timeout=0.1):
        self.arduino = serial.Serial(port=port, baudrate=baudrate, timeout=timeout)
        self.values = ['-', '+', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
        self.char_to_index = {v: i for i, v in enumerate(self.values)}  # mapowanie znak->indeks

    def write(self, index):
        value = self.values[index]
        print(value)
        self.arduino.write(value.encode('utf-8'))

    def click(self, key):
        try:
            if isinstance(key, int):
                index = key
            else:
                key = key.upper()

                if key.isdigit():
                    # normalna obsługa cyfr - znajdź indeks w values
                    if key in self.values:
                        index = self.values.index(key)
                    else:
                        raise ValueError(f"Nieznany klucz cyfrą: {key}")

                elif key in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']:
                    # dla liter przesuwamy indeks o -2 (bo 'A' to 12, chcemy 10)
                    original_index = self.values.index(key)
                    index = original_index - 1

                elif key in self.values:
                    index = self.values.index(key)
                else:
                    raise ValueError(f"Nieznany klucz: {key}")

            self.write(index)
            time.sleep(0.05)
            self.arduino.write(b'p')

        except Exception as e:
            print(f"[Arduino] Invalid input '{key}': {e}")
