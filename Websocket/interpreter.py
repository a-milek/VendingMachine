import asyncio
import json
import websockets
from ScreenInterpreter import ScreenInterpreter


interpreter = ScreenInterpreter()


async def run_client():
    uri = "ws://localhost:8765"

    print(f"Connecting to {uri} ...")

    async with websockets.connect(uri) as ws:
        print("Connected to server.")

        # Keep receiving screen updates
        while True:
            try:
                msg = await ws.recv()

                print("\n=== Received from server ===")
                print(msg)

                # Parse JSON message
                data = json.loads(msg)

                if data.get("type") != "screen_update":
                    print("Ignoring unknown message type.")
                    continue

                raw_lines = data.get("raw_lines", [])

                print("\n--- RAW LCD LINES ---")
                for line in raw_lines:
                    print(repr(line))

                # Re-interpret using your interpreter
                print("\n--- INTERPRETING LOCALLY ---")
                state = interpreter.interpret_lines(raw_lines)

                print(json.dumps(state, indent=4, ensure_ascii=False))

            except websockets.exceptions.ConnectionClosed:
                print("Disconnected from server.")
                break
            except Exception as e:
                print("Error while receiving:", e)


if __name__ == "__main__":
    asyncio.run(run_client())
