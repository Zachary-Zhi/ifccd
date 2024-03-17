from bson import ObjectId
from flask import Blueprint, request, json, current_app
from applications.common.utils.http import success_api, fail_api

change_priority_bp = Blueprint('change_priority', __name__, url_prefix='/ifccd/changePriority')

def register_change_priority_view(app):
    app.register_blueprint(change_priority_bp)


@change_priority_bp.put('/<task_id>')
def change_priority_by_task_id(task_id):

    data = request.get_data()
    json_data = json.loads(data.decode("UTF-8"))
    sequence = json_data.get("sequence")
    if sequence is None:
        return fail_api("no sequence"), 400
    try:
        ObjectId(task_id)
    except Exception as e:
        print(e)
        return fail_api("wrong task_id format"), 400

    ENHANCE_TASK_QUEUE = current_app.config.get("ENHANCE_TASK_QUEUE")
    IFCCD_TASK_QUEUE = current_app.config.get("IFCCD_TASK_QUEUE")
    enhance_flag = ENHANCE_TASK_QUEUE.change_pos_in_enhance_queue(task_id, sequence)
    ifccd_flag = IFCCD_TASK_QUEUE.change_pos_in_ifccd_queue(task_id, sequence)
    ENHANCE_TASK_QUEUE.show_que()
    IFCCD_TASK_QUEUE.show_que()
    if enhance_flag or ifccd_flag:
        return success_api("success")
    else:
        return fail_api("fail"),400
