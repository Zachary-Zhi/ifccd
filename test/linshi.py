import socket
import sys

''''# 创建 socket 对象
serversocket = socket.socket(
    socket.AF_INET, socket.SOCK_STREAM)

# 获取本地主机名
# host = socket.gethostname()
host = "10.31.227.152"
print(host)


port = 9999

# 绑定端口号
serversocket.bind((host, port))

# 设置最大连接数，超过后排队
serversocket.listen(5)

while True:
    # 建立客户端连接
    clientsocket, addr = serversocket.accept()

    print("连接地址: %s" % str(addr))

    msg = '欢迎访问菜鸟教程！' + "\r\n"
    clientsocket.send(msg.encode('utf-8'))
    clientsocket.close()'''

from flask import Flask
from flask_sockets import Sockets
import datetime

app = Flask(__name__)
sockets = Sockets(app)

from flask_cors import *
CORS(app, supports_credentials=True)

@sockets.route('/wsifccd')
def echo_socket(ws):
    print("hello")
    while not ws.closed:
        msg = ws.receive()
        print(msg)
        now = datetime.datetime.now().isoformat()
        ws.send(now)  #发送当前时间数据


if __name__ == "__main__":
    from gevent import pywsgi
    from geventwebsocket.handler import WebSocketHandler
    server = pywsgi.WSGIServer(('0.0.0.0', 8080), app, handler_class=WebSocketHandler)
    print('server start')
    server.serve_forever()




 # from gevent import pywsgi
    # from geventwebsocket.handler import WebSocketHandler
    # server = pywsgi.WSGIServer(('127.0.0.1', 9000), app, handler_class=WebSocketHandler)
    # print('server start')   #运行socket服务器
    #server.serve_forever()

# from flask_sockets import Sockets
# import datetime
# sockets = Sockets(app)
# from flask_cors import *
# CORS(app, supports_credentials=True)
#
# @sockets.route('/wsifccd')
# def echo_socket(ws):
#     print("hello")
#     while not ws.closed:
#         msg = ws.receive()
#         print(msg)
#         now = datetime.datetime.now().isoformat()
#         ws.send(now)  #发送当前时间数据