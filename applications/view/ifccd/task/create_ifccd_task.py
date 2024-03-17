import os

from flask import Blueprint, request, json, current_app

from applications.common.utils.http import success_api, fail_api
from applications.models import Task
from applications.reposity.task_reposity import insert_task
from applications.option.options import task_executing_dic
from applications.option.options import task_executing_dic, docker_map_url_prefix
from applications.common.utils.path_operate import url_map
from applications.option import options

create_ifccd_task_bp = Blueprint('create_ifccd_task', __name__, url_prefix='/ifccd/ifccdTasks')

@create_ifccd_task_bp.post('')
def create_ifccd_task():

    IFCCD_TASK_QUEUE = current_app.config.get("IFCCD_TASK_QUEUE")
    print(IFCCD_TASK_QUEUE)
    data = request.get_data()
    json_data = json.loads(data.decode("UTF-8"))
    print(json_data)
    user_name = json_data.get("user")
    if user_name is None:
        return fail_api("no user"), 400
    if json_data.get("import") is None:
        return fail_api("no import url"), 400
    if json_data.get("georeference") is None:
        return fail_api("no georeference information"), 400
    if json_data.get("georeference").get("algName") is None:
        return fail_api("no groreference algName"), 400
    if json_data.get("fusion") and json_data.get("fusion").get("algName") is None:
        return fail_api("no fusion algName"), 400
    if json_data.get("detect") and json_data.get("detect").get("algName") is None:
        return fail_api("no detect algName"), 400
    if json_data.get("fusion") and json_data.get("detect"):
        return fail_api("ifccd task can only contain one of fusion and detect"), 400
    input_names = json_data.get("import")
    for input_name in input_names:
        if os.path.exists(docker_map_url_prefix + url_map(input_name)):
            print("文件存在")
        else:
            print("文件不存在")
            return fail_api("file not found"), 400

    taskClassesType = "georeference"
    if json_data.get("fusion"):
        taskClassesType = "fusion"
    if json_data.get("detect"):
        taskClassesType = "detect"
    res_task_algName = ""
    task_algName = json_data.get("georeference").get("algName")
    res_task_algName = res_task_algName + task_algName
    if taskClassesType == "georeference":
        task_algName = json_data.get("georeference").get("algName")
        res_task_algName = res_task_algName + task_algName
    elif taskClassesType == "fusion":
        task_algName = json_data.get("fusion").get("algName")
        res_task_algName = res_task_algName + " " + task_algName
    elif taskClassesType == "detect":
        task_algName = json_data.get("detect").get("algName")
        res_task_algName = res_task_algName + " " + task_algName
    else:
        print("error task_algName")
        return fail_api("error task_algName"), 400

    task = Task(user_name=user_name, task_params_json=json_data, task_status=0, task_type="1", taskClassesType=taskClassesType, task_algName=res_task_algName)
    task_json = task.class_to_json()
    task_id = insert_task(task.json_to_dic(task_json))
    task.task_id = task_id

    single_task_executing_dic = {}
    single_task_executing_dic["taskId"] = task_id
    single_task_executing_dic["taskStage"] = "waiting for execute"
    single_task_executing_dic["completeRate"] = 0
    single_task_executing_dic["task_algName"] = res_task_algName
    task_executing_dic[str(task_id)] = single_task_executing_dic

    IFCCD_TASK_QUEUE.add_ifccd_task_to_queue(task)
    IFCCD_TASK_QUEUE.show_que()

    return success_api("success")
