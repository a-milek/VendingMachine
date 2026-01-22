import os
import socket

from bottle import route, run, static_file, request, response
import json

PING_INTERVAL = 5
PING_ENABLED = False
TELEGRAF_HOST = "0.0.0.0"
TELEGRAF_PORT = 8094

COUNTERS_FILE = "cntrs.json"
COUNTERS_FILE_BACKUP = "cntrs_backup.json"
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


def send_to_telegraf(line):
    sock.sendto(line.encode("utf-8"), (TELEGRAF_HOST, TELEGRAF_PORT))


def load_counters():
    if os.path.exists(COUNTERS_FILE):
        with open(COUNTERS_FILE, "r") as f:
            return json.load(f)
    return {}


def save_counters(counters):
    with open(COUNTERS_FILE_BACKUP, "w") as f:
        json.dump(counters, f, indent=2)
    os.replace(COUNTERS_FILE_BACKUP,COUNTERS_FILE)


product_counters = load_counters()


@route('/statservice/order_complete', method='POST')
def statistics_update():
    data = request.json
    if not data or "product_id" not in data:
        response.status = 400
        return {"error": "Missing product_id"}

    product_id = str(data["product_id"])

    product_counters[product_id] = product_counters.get(product_id, 0) + 1

    save_counters(product_counters)

    total_count = product_counters[product_id]
    message = f"coffee_event,product_id={product_id} count={total_count}"
    send_to_telegraf(message)
    print(f"Order received for product_id: {product_id}, total: {total_count}")
    return {"product_id": product_id, "total": total_count}




if __name__ == '__main__':
    run(host="0.0.0.0", port=8081, debug=True)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
