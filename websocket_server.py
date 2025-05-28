import asyncio
import websockets

connected_clients = set()

async def echo(websocket, path):
    connected_clients.add(websocket)
    try:
        async for message in websocket:
            print(f"Received: {message}")
            await websocket.send(f"Echo: {message}")
    finally:
        connected_clients.remove(websocket)

start_server = websockets.serve(echo, "localhost", 8765)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
