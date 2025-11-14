import time
import serial

class Arduino:
    def __init__(self,  port='/dev/serial/by-path/platform-xhci-hcd.1-usb-0:2:1.0-port0', baudrate=9600, timeout=0.1):
        self.arduino = serial.Serial(port=port, baudrate=baudrate, timeout=timeout)
        self.values = ['-', '+', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H','I']

    def write(self, index):
        value = self.values[index]
        print(f"Sending index {index} → '{value}'")
        self.arduino.write(value.encode('utf-8'))

    def click_by_index(self, index):
        self.write(index)
        time.sleep(0.05)
        self.arduino.write(b'p')

    def click_by_key(self, key):

        if key not in self.values:
            raise ValueError(f"Nieznany klawisz: {key}")
        index = self.values.index(key)
        self.click_by_index(index)

    def ping(self):
        try:
            # Send a ping character (anything not used: '#' is safe)
            self.arduino.write(b'#')


            return True

        except Exception as e:
            raise Exception(f"Arduino ping failed: {e}")

