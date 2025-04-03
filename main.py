import threading
import time

from bottle import route, run, static_file, request

import sys
import os
from BUSofPCF8574 import BUSofPCF8574

pc=BUSofPCF8574()

@route('/pomodoro-app/<filepath:path>')
def server_static(filepath):
    return static_file(filepath, root='C:/Users/Ania/Downloads/github-pages/artifact')


@route('/vending-machines/<filepath:path>')
def server_static(filepath):
    return static_file(filepath, root='./dist')


@route('/vending-machines/order', method='POST')
def order():
    data = request.json
    print("Order:", data)
    if data:
        print("Id:", data["coffeeId"])
        pc.click(data["coffeeId"])


    return "{}"


def run_server():
    run(host="0.0.0.0", port=8080, debug=True)




if __name__ == '__main__':
    run_server()
