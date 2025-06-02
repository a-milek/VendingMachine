import sys
import traceback
import serial
import json
from serial.threaded import LineReader, ReaderThread
import websockets
import asyncio

connected_clients = set()
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)  # For access across threads

# Store received lines in a list
received_lines = []


class PrintLines(LineReader):
    def connection_made(self, transport):
        super(PrintLines, self).connection_made(transport)
        sys.stdout.write('Serial port opened\n')

    def handle_line(self, data):
        sys.stdout.write(f'Line received: {repr(data)}\n')

        product_version = [
            "Wybierz produkt",
            "ybierz produkt     W",
            "bierz produkt     Wy",
            "ierz produkt     Wyb",
            "erz produkt     Wybi",
            "rz produkt     Wybie",
            "z produkt     Wybier",
            "produkt     Wybierz",
            "rodukt     Wybierz p",
            "odukt     Wybierz pr",
            "dukt     Wybierz pro",
            "ukt     Wybierz prod",
            "kt     Wybierz produ",
            "t    Wybierz produku",
            "t     Wybierz produk",
        ]

        # Normalize the line
        if any(fragment in data for fragment in product_version):
            received_lines.append("Wybierz produkt")
        else:
            received_lines.append(data.strip())

        # If we have at least 4 lines, send the first 4 and remove them
        while len(received_lines) >= 4:
            combined_data = "\n".join(received_lines[:4])
            print("Sending to clients:", combined_data)
            asyncio.run_coroutine_threadsafe(
                send_to_all_clients(json.dumps({
                    "type": "serial",
                    "message": combined_data
                })),
                loop
            )
            # Remove the sent lines
            del received_lines[:4]

    def connection_lost(self, exc):
        if exc:
            traceback.print_exc()
        sys.stdout.write('Serial port closed\n')


# Use your actual serial port here
ser = serial.Serial('/dev/serial/by-path/platform-xhci-hcd.0-usb-0:2:1.0-port0', baudrate=230440, timeout=1)


async def websocket_handler(websocket):
    print("Client connected")
    connected_clients.add(websocket)
    try:
        async for message in websocket:
            print("📨 Received from client:", message)
    except websockets.exceptions.ConnectionClosed:
        print("Client disconnected")
    finally:
        connected_clients.remove(websocket)


async def start_websocket_server():
    print("Starting WebSocket server on ws://localhost:8765/")
    return await websockets.serve(websocket_handler, "localhost", 8765)


async def send_to_all_clients(message):
    if connected_clients:
        await asyncio.gather(*[client.send(message) for client in connected_clients])


if __name__ == "__main__":
    with ReaderThread(ser, PrintLines) as protocol:
        # Start the WebSocket server
        ws_server = loop.run_until_complete(start_websocket_server())

        try:
            loop.run_forever()
        except KeyboardInterrupt:
            print("Shutting down...")
        finally:
            ws_server.close()
            loop.run_until_complete(ws_server.wait_closed())
            loop.stop()
