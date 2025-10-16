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
        if isinstance(serv_id, str):
            serv_id = serv_id.upper()  # na wypadek małych liter

            if serv_id.isdigit():
                index = int(serv_id)
            elif 'A' <= serv_id <= 'H':
                index = 10 + ord(serv_id) - ord('A')  # A→10, B→11, ..., H→17
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
        os._exit(1)
        return True



# Run the server
def run_server():
    run(host="0.0.0.0", port=8080, debug=True)


if __name__ == '__main__':
    run_server()
