import threading
import time
import socket
import traceback

from bottle import route, run, static_file, request, response, Bottle, redirect
from Arduino import Arduino
import sys
import os
import json
import pika
import requests
from bottle import route, request, response

arduino = Arduino(port=os.getenv("VENDING_MACHINE_DEVICE_SERIAL_KEYBOARD") )

app = Bottle()

PING_INTERVAL = 5
PING_ENABLED = False

# Coffee list (names, prices, servIds, images) edited from the kiosk's tech mode.
# Kept outside the repo so git pull / dev-update never overwrite it.
COFFEE_DATA = os.path.expanduser(
    os.getenv("VENDING_MACHINE_COFFEE_DATA", "~/vending-data/coffee-data.json")
)




# -------------------------------
# Arduino ping thread
# -------------------------------
def arduino_ping_loop():
    while PING_ENABLED:
        try:
            arduino.ping()  # ping using echo (#)

            print("[PING] Arduino OK")

        except Exception as e:
            print(f"Error while sending command to Arduino: {e}")
            traceback.print_exc()
            os._exit(1)
            return True  # unreachable

        time.sleep(PING_INTERVAL)


# -------------------------------
# Bottle routes
# -------------------------------
@route('/pomodoro-app/<filepath:path>')
def serve_pomodoro(filepath):
    return static_file(filepath, root='C:/Users/Ania/Downloads/github-pages/artifact')


# Must be defined before the static catch-all below, which would otherwise match it
@route('/vending-machines/coffee-data', method='GET')
def get_coffee_data():
    response.headers['Cache-Control'] = 'no-store'
    if not os.path.exists(COFFEE_DATA):
        # Nothing saved yet: the UI then uploads its own list
        response.status = 404
        return {"error": "No coffee data saved yet"}
    response.content_type = 'application/json'
    with open(COFFEE_DATA, encoding='utf-8') as f:
        return f.read()


@route('/vending-machines/coffee-data', method='PUT')
def put_coffee_data():
    try:
        data = request.json
        if not isinstance(data, list) or not all(
            isinstance(c, dict) and "servId" in c and "price" in c and "name" in c
            for c in data
        ):
            raise ValueError(f"Invalid coffee data: {data!r}")

        # Write to a temp file and swap it in, so a crash never leaves half a file
        os.makedirs(os.path.dirname(COFFEE_DATA), exist_ok=True)
        tmp = COFFEE_DATA + ".tmp"
        with open(tmp, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, COFFEE_DATA)
        print(f"Coffee data saved to {COFFEE_DATA} ({len(data)} items)")
        return {"saved": len(data)}

    except Exception as e:
        print(f"Error while saving coffee data: {e}")
        traceback.print_exc()
        os._exit(1)


@route('/vending-machines/<filepath:path>')
def serve_vending(filepath):
    return static_file(filepath, root='./dist')

@route('/vending-machines/statservice/order_complete', method=['POST', 'OPTIONS'])
def statservice_proxy():
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    if request.method == 'OPTIONS':
        return

    r = requests.post(
        "http://localhost:8081/statservice/order_complete",
        json=request.json
    )
    response.status = r.status_code
    return r.content


@route('/vending-machines/order', method='POST')
def handle_order():
    data = request.json
    if not data or "servId" not in data:
        response.status = 400
        return {"error": "Missing servId"}

    serv_id = data["servId"]

    print("Order received with servId:", serv_id)

    try:
        if isinstance(serv_id, str):
            serv_id = serv_id.upper()

            if serv_id.isdigit():
                index = int(serv_id)
            elif 'A' <= serv_id <= 'H':
                index = 10 + ord(serv_id) - ord('A')
            elif serv_id == '+':
                index = 1
            elif serv_id == '-':
                index = 0
            else:
                raise ValueError(f"Nieznany servId: {serv_id}")
        else:
            index = int(serv_id)

        arduino.click_by_index(index)


        return True

    except Exception as e:
        print(f"Error while sending command to Arduino: {e}")
        traceback.print_exc()
        os._exit(1)
        return True


def run_server():
    threading.Thread(target=arduino_ping_loop, daemon=True).start()
    run(host="0.0.0.0", port=8080, debug=True)


if __name__ == '__main__':
    run_server()
