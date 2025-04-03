## Detecting i2C
amilek@raspberrypi:~ $ i2cdetect -y 1
     0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
00:                         -- -- -- -- -- -- -- -- 
10: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
20: 20 21 -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
30: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
40: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
50: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
60: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
70: -- -- -- -- -- -- -- --   

## I2C not connected
amilek@raspberrypi:~/Documents/Server $ journalctl -f
Apr 03 15:06:53 raspberrypi serverscript.sh[3825]:   File "/home/amilek/Documents/Server/BUSofPCF8574.py", line 17, in click
Apr 03 15:06:53 raspberrypi serverscript.sh[3825]:     device.click(channel % 8)
Apr 03 15:06:53 raspberrypi serverscript.sh[3825]:   File "/home/amilek/Documents/Server/PCF8574.py", line 38, in click
Apr 03 15:06:53 raspberrypi serverscript.sh[3825]:     self.set_channel(channel, 1)
Apr 03 15:06:53 raspberrypi serverscript.sh[3825]:   File "/home/amilek/Documents/Server/PCF8574.py", line 35, in set_channel
Apr 03 15:06:53 raspberrypi serverscript.sh[3825]:     self.bus.write_byte(self.address, self.current_msg)
Apr 03 15:06:53 raspberrypi serverscript.sh[3825]:   File "/home/amilek/Documents/Server/myenv/lib/python3.11/site-packages/smbus2/smbus2.py", line 416, in write_byte
Apr 03 15:06:53 raspberrypi serverscript.sh[3825]:     ioctl(self.fd, I2C_SMBUS, msg)
Apr 03 15:06:53 raspberrypi serverscript.sh[3825]: OSError: [Errno 5] Input/output error
Apr 03 15:06:53 raspberrypi serverscript.sh[3825]: 127.0.0.1 - - [03/Apr/2025 15:06:53] "POST /vending-machines/order HTTP/1.1" 500 1996


