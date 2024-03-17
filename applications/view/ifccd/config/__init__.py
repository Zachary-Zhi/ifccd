from flask import Blueprint, request, json
from applications.common.utils.http import success_api
from applications.common.utils.path_operate import url_map_with_slash
import os
from applications.option.options import net_url_prefix
config_bp = Blueprint('config', __name__, url_prefix='/ifccd/config')


def register_config_view(app):
    app.register_blueprint(config_bp)


@config_bp.put('/')
def change_configuration():
    data = request.get_data()
    json_data = json.loads(data.decode("UTF-8"))
    print(json_data)
    save_path = json_data.get("savePath")
    web_socket_server = json_data.get("webSocketServer")
    if save_path == None:
        save_path = ""
    if web_socket_server == None:
        web_socket_server = ""

    print("从请求体中获取的属性： savePath: " + save_path, "\twebSocketServer: " + web_socket_server)
    print("当前环境中的属性： savePath: " + net_url_prefix + os.getenv('SAVE_PATH'), "\twebSocketServer: " + os.getenv('WEBSOCKET_SERVER'))
    if not save_path == "":
        print('save_path not null')
        print(url_map_with_slash(save_path))
        os.environ["SAVE_PATH"] = url_map_with_slash(save_path)
    if not web_socket_server == "":
        os.environ["WEBSOCKET_SERVER"] = web_socket_server
    print("更改后环境中的属性： savePath: " + net_url_prefix + os.getenv('SAVE_PATH'), "\twebSocketServer: " + os.getenv('WEBSOCKET_SERVER'))
    return success_api("success")
