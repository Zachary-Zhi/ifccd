from bson import ObjectId
from flask import Blueprint, current_app
from applications.common.utils.http import success_api, fail_api
from applications.reposity.task_reposity import update_task_status_by_task_id, select_task_by_task_id
stop_task_bp = Blueprint('stop_task_bp', __name__, url_prefix='/ifccd/tasks')

@stop_task_bp.delete('/<task_id>')
def stop_task(task_id):

    task_id = str(task_id)
    try:
        ObjectId(task_id)
    except Exception as e:
        print(e)
        return fail_api("wrong task_id format"), 400

    ENHANCE_TASK_QUEUE = current_app.config.get("ENHANCE_TASK_QUEUE")
    IFCCD_TASK_QUEUE = current_app.config.get("IFCCD_TASK_QUEUE")
    tmp_task_dic = select_task_by_task_id(task_id)
    if tmp_task_dic is None:
        return fail_api("no such task_id"), 400
    if tmp_task_dic.get("task_status") == 3:
        return fail_api("task has been stopped"), 400
    elif tmp_task_dic.get("task_status") == 2:
        return fail_api("task is executing, can't be stopped"), 400
    elif tmp_task_dic.get("task_status") == 1:
        return fail_api("task has been executed"), 400
    enhance_flag = ENHANCE_TASK_QUEUE.delete_from_enhance_task_queue(task_id)
    ifccd_flag = IFCCD_TASK_QUEUE.delete_from_ifccd_task_queue(task_id)
    update_task_status_by_task_id(task_id, 1)
    if enhance_flag or ifccd_flag:
        return success_api("success")
    else:
        return fail_api("stop task fail"), 400