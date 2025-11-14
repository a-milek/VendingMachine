import sys
import threading
import traceback
import serial
import json
from serial.threaded import LineReader, ReaderThread
import websockets
import asyncio
import time
import os

connected_clients = set()
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)  # For access across threads
screen_state_json = None

class PrintLines(LineReader):
    def __init__(self):
        super().__init__()

        self.receiving = False
        self.received_lines = []
        self.lines_to_collect = 0


    def connection_made(self, transport):
        super(PrintLines, self).connection_made(transport)
        sys.stdout.write('Serial port opened\n')

    def handle_line(self, data):
        global screen_state_json
        try:
            sys.stdout.write(f'Line received: {repr(data)}\n')
            line = data.strip()

            if "LCD Proper" in line:
                self.received_lines = []
                self.receiving = True
                self.lines_to_collect = 4  # start collecting 4 lines AFTER "LCD Proper"
                return

            if self.receiving:
                self.received_lines.append(line)
                self.lines_to_collect -= 1

                if self.lines_to_collect == 0:
                    combined_data = "\n".join(self.received_lines)
                    print("Sending to clients:", repr(combined_data))

                    screen_state_json=json.dumps({
                            "type": "serial",
                            "message": combined_data
                        })

                    self._send_screen_state_to_clients()
                    self.received_lines = []
                    self.receiving = False
        except Exception:
            print("Exception in handle_line:")
            traceback.print_exc()

    def _send_screen_state_to_clients(self):
        asyncio.run_coroutine_threadsafe(
            send_to_all_clients(screen_state_json),
            loop
        )


    def connection_lost(self, exc):
        print("Connection lost called")
        if exc:
            print("Exception during connection lost:")
            traceback.print_exc()
        sys.stdout.write('Serial port closed\n')
        os._exit(1)

async def websocket_handler(websocket):
    print("Client connected")
    connected_clients.add(websocket)
    if screen_state_json:
        await websocket.send(screen_state_json)



    try:
        async for message in websocket:
            print("Received from client:", message)
    except websockets.exceptions.ConnectionClosed:
        print("Client disconnected")
    finally:
        connected_clients.remove(websocket)


async def start_websocket_server():
    # test
    print("Starting WebSocket server on ws://localhost:8765/")
    return await websockets.serve(websocket_handler,  "0.0.0.0", 8765)

async def send_to_all_clients(message):
    if connected_clients:
        await asyncio.gather(*[client.send(message) for client in connected_clients])

def main():
    ser = serial.Serial('/dev/serial/by-path/platform-xhci-hcd.0-usb-0:2:1.0-port0', baudrate=230440, timeout=1)

    while True:
        try:
            with ReaderThread(ser, PrintLines):
                # Start the WebSocket server once per program run
                ws_server = loop.run_until_complete(start_websocket_server())
                print("WebSocket server running.")
                loop.run_forever()
        except Exception as e:
            print(f"Exception in main loop: {e}")
            traceback.print_exc()
            print("Restarting serial connection after 3 seconds...")
            time.sleep(3)
        finally:
            try:
                ser.close()
                print("Serial port closed in finally.")
            except Exception as e:
                print(f"Error closing serial port: {e}")

if __name__ == "__main__":
    main()
