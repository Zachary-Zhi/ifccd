from flask import Blueprint
from applications.common.utils.http import success_api, fail_api
from applications.reposity.task_reposity import select_tasks_by_status, update_task_status_by_task_id
from applications.common.enum.task_status_enum import task_status_enum

logical_delete_bp = Blueprint('logical_delete_bp', __name__, url_prefix='/ifccd/excise')


@logical_delete_bp.get('')
def logical_delete():
    try:
        results_list = list(select_tasks_by_status(1))
        for tmp_task in results_list:
            update_task_status_by_task_id(tmp_task.get("_id"), 6)
    except Exception as e:
        return fail_api("fail"), 400
    return success_api("success"), 200
