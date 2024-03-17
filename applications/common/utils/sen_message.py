import json
import time
import os
from websocket import create_connection
#用之前装一下 websocket-client/websocket-client2
WEBSOCKET_IP = os.getenv("WEBSOCKET_IP")
if WEBSOCKET_IP is None:
    WEBSOCKET_IP = "192.168.8.143"
WEBSOCKET_PORT = os.getenv("WEBSOCKET_PORT")
if WEBSOCKET_PORT is None:
    WEBSOCKET_PORT = "5001"
WEBSOCKET_URL = os.getenv("WEBSOCKET_URL")
if WEBSOCKET_URL is None:
    WEBSOCKET_URL = "wsIFCCD"
ws_url = "ws://" + str(WEBSOCKET_IP) + ":" + str(WEBSOCKET_PORT) + "/" + str(WEBSOCKET_URL)


def send_message(TaskId, Owner, Info, Result, Err, import_list = None):
    print("websocket send")
    print(ws_url)
    try:                
        ws = create_connection(ws_url)
        # 构造消息字典
        msg = {
            'taskid': str(TaskId),
            'owner': str(Owner),
            'info': str(Info),
            'result': Result,
            'err': str(Err),
            'import':import_list
        }
        print(msg)
        # 如果 Result 为 0，删除 result 键
        if str(Result) == '0':
            del msg['result']

        if ws.connected:
            content = json.dumps(msg, indent=2, sort_keys=True, ensure_ascii=False)
            ws.send(content)
            print(content)
            time.sleep(1)
            ws.close()
    except:
        print("websocket send error, msg: " + msg)
