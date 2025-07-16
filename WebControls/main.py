import threading
import time

from bottle import route, run, static_file, request, response
from Arduino import Arduino
import sys
import os

arduino = Arduino()


@route('/pomodoro-app/<filepath:path>')
def serve_pomodoro(filepath):
    return static_file(filepath, root='C:/Users/Ania/Downloads/github-pages/artifact')


@route('/vending-machines/<filepath:path>')
def serve_vending(filepath):
    return static_file(filepath, root='./dist')


@route('/vending-machines/order', method='POST')
def handle_order():
    data = request.json
    if not data or "servId" not in data:
        response.status = 400
        return {"error": "Missing servId"}

    serv_id = data["servId"]

    print("Order received with servId:", serv_id)

    try:

        arduino.click(serv_id)
        return {"status": "OK", "received": serv_id}
    except Exception as e:
        print("Error while sending command to Arduino:", e)
        response.status = 500
        return {"error": str(e)}


# Run the server
def run_server():
    run(host="0.0.0.0", port=8080, debug=True)


if __name__ == '__main__':
    run_server()
