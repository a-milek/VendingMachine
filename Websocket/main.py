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
reset_flag = False  # Flag to indicate if reset is needed when "LCD Proper" is received


class PrintLines(LineReader):
    def connection_made(self, transport):
        super(PrintLines, self).connection_made(transport)
        sys.stdout.write('Serial port opened\n')

    def handle_line(self, data):
        sys.stdout.write(f'Line received: {repr(data)}\n')
        set_done = False
        # Process and send the message only if it's valid
        if "LCD Proper" in data:
            set_done = True
            # break
            # Reset the received lines and start a new message
            # received_lines.clear()

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

        if any(fragment in data for fragment in product_version):
            received_lines.append("Wybierz produkt")
        else:
            received_lines.append(data.strip())

        # If we have 5 lines, send them to WebSocket clients
        if set_done:
            combined_data = "\n".join(received_lines)
            print("Sending to clients:", combined_data)  # Add this log to check what is sent
            asyncio.run_coroutine_threadsafe(
                send_to_all_clients(json.dumps({
                    "type": "serial",
                    "message": combined_data
                })),
                loop
            )
            received_lines.clear()  # Reset for next batch

    def connection_lost(self, exc):
        if exc:
            traceback.print_exc()
        sys.stdout.write('Serial port closed\n')


# Use COM5 (change if needed)
ser = serial.Serial('/dev/ttyUSB0', baudrate=230440, timeout=1)


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
