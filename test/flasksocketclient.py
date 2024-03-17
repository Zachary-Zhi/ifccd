from time import sleep
import sys
import os
import websockets

ws = websockets.connect("ws://127.0.0.1/test")
def send_query_webSocket():
    while True:
        input_text = "ping"
        ws.send(input_text)
        output_text = ws.recv()
        print("receive msg: ", output_text)
        sleep(1)


if __name__ == '__main__':
    send_query_webSocket()