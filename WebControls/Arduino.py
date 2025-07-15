#!/usr/bin/python

import time
import serial


class Arduino:
    def __init__(self, port='/dev/serial/by-path/platform-xhci-hcd.1-usb-0:2:1.0-port0', baudrate=9600, timeout=0.1):
        # self.arduino = serial.Serial(port=port, baudrate=baudrate, timeout=timeout)
        self.values = ['-','+','1','2','3','4','5','6','7','8','9','A','B','C','D','E','F','G','H']

    def write(self, index):
        value = self.values[index]
        print(value)
        self.arduino.write(value.encode('utf-8'))

    def click(self, key):
        try:
            # Jeśli key jest liczbą lub stringiem liczbowym - używamy go jako indeksu
            if isinstance(key, int):
                index = key
            else:
                # Jeśli string, sprawdzamy czy jest cyfrą
                if key.isdigit():
                    index = int(key)
                else:
                    # jeśli nie jest cyfrą, to traktujemy jako znak i szukamy indeksu w self.values
                    key = key.upper()  # dla pewności
                    if key in self.values:
                        index = self.values.index(key)
                    else:
                        raise ValueError(f"Nieznany klucz: {key}")

            self.write(index)  # write oczekuje indeksu
            time.sleep(0.05)
            self.arduino.write(b'p')

        except (ValueError, IndexError, TypeError) as e:
            print(f"[Arduino] Invalid input '{key}': {e}")

