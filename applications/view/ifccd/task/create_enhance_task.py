import os
from flask_cors import *
from flask import Blueprint, request, json, current_app
from applications.common.utils.http import success_api, fail_api
from applications.models import Task
from applications.reposity.task_reposity import insert_task
from applications.option.options import task_executing_dic, docker_map_url_prefix, docker_map_url_enhance_prefix
from applications.option import options
from applications.common.utils.path_operate import url_map
create_enhance_task_bp = Blueprint('create_enhance_task', __name__, url_prefix='/ifccd/enhance')

@create_enhance_task_bp.post('')
@cross_origin(supports_credentials=True)
def create_enhance_task():

    ENHANCE_TASK_QUEUE = current_app.config.get("ENHANCE_TASK_QUEUE")
    print(type(ENHANCE_TASK_QUEUE))
    print(ENHANCE_TASK_QUEUE)
    data = request.get_data()
    json_data = json.loads(data.decode("UTF-8"))
    print(json_data)
    user_name = json_data.get("user")
    if user_name is None:
        return fail_api("no user"), 400
    if json_data.get("import") is None:
        return fail_api("no import url"), 400
    if json_data.get("alg") is None:
        return fail_api("no alg"), 400
    if json_data.get("alg") and json_data.get("alg").get("algName") is None:
        return fail_api("no alg algName"), 400
    if json_data.get("alg") and json_data.get("alg").get("algType") is None:
        return fail_api("no alg algType"), 400
    input_name = json_data.get("import")
    url_map_in_docker = docker_map_url_enhance_prefix + url_map(input_name)
    print(url_map_in_docker)
    if os.path.exists(url_map_in_docker):
        print("文件存在")
    else:
        print("文件不存在")
        return fail_api("file not found"), 400
    
    task = Task(user_name=user_name, task_params_json=json_data, task_status=0, task_type="0", taskClassesType=json_data.get("alg").get("algType"), task_algName=json_data.get("alg").get("algName"))
    task_json = task.class_to_json()
    task_id = insert_task(task.json_to_dic(task_json))
    task.task_id = task_id

    single_task_executing_dic = {}
    single_task_executing_dic["taskId"] = task_id
    single_task_executing_dic["taskStage"] = "waiting for execute"
    single_task_executing_dic["completeRate"] = 0
    single_task_executing_dic["task_algName"] = json_data.get("alg").get("algName")

    task_executing_dic[str(task_id)] = single_task_executing_dic
    ENHANCE_TASK_QUEUE.add_enhance_task_to_queue(task)
    ENHANCE_TASK_QUEUE.show_que()

    return success_api("success")

