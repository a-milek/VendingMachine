import asyncio
import json
import websockets
from ScreenInterpreter import ScreenInterpreter

interpreter = ScreenInterpreter()


def extract_lines_from_message(data):
    """
    Converts both message formats into a clean list of LCD lines.
    """

    if data.get("type") == "screen_update":
        # Already formatted
        return data.get("raw_lines", [])

    elif data.get("type") == "serial":
        # Raw multiline string
        msg = data.get("message", "")

        # Split into lines
        lines = msg.split("\n")

        # Strip whitespace, ignore empty lines
        lines = [line.rstrip() for line in lines if line.strip() != ""]

        return lines

    return []


async def run_client():
    uri = "ws://localhost:8765"
    print(f"Connecting to {uri} ...")

    async with websockets.connect(uri) as ws:
        print("Connected to server.")

        while True:
            try:
                msg = await ws.recv()
                data = json.loads(msg)

                print("\n=== Received from server ===")
                print(msg)

                # Extract LCD lines from whichever format arrived
                raw_lines = extract_lines_from_message(data)

                if not raw_lines:
                    print("No LCD lines found.")
                    continue

                print("\n--- RAW LCD LINES ---")
                for line in raw_lines:
                    print(repr(line))

                # Interpret with your interpreter
                state = interpreter.interpret_lines(raw_lines)

                print("\n--- INTERPRETED STATE ---")
                print(json.dumps(state, indent=4, ensure_ascii=False))

            except websockets.exceptions.ConnectionClosed:
                print("Disconnected from server.")
                break
            except Exception as e:
                print("Error:", e)


if __name__ == "__main__":
    asyncio.run(run_client())
