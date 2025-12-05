import asyncio
import json
import websockets
from ScreenInterpreter import ScreenInterpreter

# ----------------------------
# CONFIG
# ----------------------------
VENDING_WS_URL = "ws://localhost:8765"       # Vending machine WS
REACT_LISTEN_PORT = 3001                    # React WS server port
# ----------------------------

interpreter = ScreenInterpreter()

# Connected React clients
react_clients = set()


def extract_lines_from_message(data):
    if data.get("type") == "screen_update":
        return data.get("raw_lines", [])

    elif data.get("type") == "serial":
        msg = data.get("message", "")
        lines = [line.strip() for line in msg.split("\n") if line.strip() != ""]
        return lines

    return []


async def broadcast_to_react(state):
    """
    Sends interpreted LCD state to ALL connected React clients.
    """
    if not react_clients:
        return

    message = json.dumps({
        "type": "interpreted_state",
        "state": state
    })

    await asyncio.gather(*(client.send(message) for client in react_clients))


# ----------------------------------------------------
# React WebSocket server (frontend connects here)
# ----------------------------------------------------
async def react_handler(websocket):
    print("React client connected")
    react_clients.add(websocket)

    try:
        async for _ in websocket:
            pass  # React usually doesn't send messages
    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        print("React client disconnected")
        react_clients.remove(websocket)


async def start_react_server():
    print(f"Starting React WebSocket server on ws://0.0.0.0:{REACT_LISTEN_PORT}")
    return await websockets.serve(react_handler, "0.0.0.0", REACT_LISTEN_PORT)


# ----------------------------------------------------
# Vending machine WS client
# ----------------------------------------------------
async def vending_client():
    print(f"Connecting to vending WS: {VENDING_WS_URL}")

    async with websockets.connect(VENDING_WS_URL) as machine_ws:
        print("Connected to vending machine WS.")

        while True:
            try:
                msg = await machine_ws.recv()
                data = json.loads(msg)

                print("\n=== Received from vending machine ===")
                print(msg)

                raw_lines = extract_lines_from_message(data)

                if not raw_lines:
                    print("No LCD lines found.")
                    continue

                print("\n--- RAW LCD LINES ---")
                for line in raw_lines:
                    print(repr(line))

                state = interpreter.interpret_lines(raw_lines)

                print("\n--- INTERPRETED STATE ---")
                print(json.dumps(state, indent=4, ensure_ascii=False))

                await broadcast_to_react(state)

            except websockets.exceptions.ConnectionClosed:
                print("Disconnected from vending WS.")
                break
            except Exception as e:
                print("Error:", e)


# ----------------------------------------------------
# MAIN LOOP: runs vending client + React server together
# ----------------------------------------------------
async def main():
    await start_react_server()

    await vending_client()


if __name__ == "__main__":
    asyncio.run(main())
