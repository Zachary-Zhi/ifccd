from flask import Blueprint, jsonify
from applications.common.utils.http import success_api, fail_api
from bson.objectid import ObjectId
from applications.reposity.task_reposity import select_task_by_task_id
select_logs_by_taskid_bp = Blueprint('select_logs_by_taskid_bp', __name__, url_prefix='/ifccd/log')

@select_logs_by_taskid_bp.get('<taskid>')
def select_logs_by_taskid(taskid):
    if taskid is None:
        return fail_api("no taskid"), 400
    try:
        ObjectId(str(taskid))
    except Exception as e:
        print("not a valid ObjectId")
        return fail_api("not a valid ObjectId"), 400
    if select_task_by_task_id(taskid) is None:
        print("is None")
        return fail_api("error task_id"), 400
    try:
        test_dic=select_task_by_task_id(taskid)["logs"]
    except Exception as e:
        print("error in find in db")
        return fail_api("error in find in db"), 400

    res_list = [] # 函数返回的list
    results_list = [] # 存储查询数据库的结果
    for logdic in test_dic:
        results_list.append(logdic)

    for log_dic in results_list:
        log_time = log_dic.get("beginTime")

        res_single_task_dic = {}
        res_single_task_dic["beginTime"] = log_time
        res_single_task_dic["endTime"] = log_dic.get("endTime")
        res_single_task_dic["user"] = log_dic.get("user")
        res_single_task_dic["import"] = log_dic.get("import")
        res_single_task_dic["output"] = log_dic.get("output")
        res_single_task_dic["taskType"] = log_dic.get("taskType")
        res_single_task_dic["taskId"] = log_dic.get("taskId")
        res_single_task_dic["taskstage"] = log_dic.get("taskstage")
        res_single_task_dic["taskClassesType"] = log_dic.get("taskClassesType")
        res_list.append(res_single_task_dic)

    for tmp in res_list:
        print(tmp)
        print("===============")
    return jsonify(res_list)
