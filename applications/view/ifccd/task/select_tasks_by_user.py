import pymongo
from flask import Blueprint, request, json, current_app, jsonify
from applications.common.utils.http import fail_api
from applications.reposity.task_reposity import select_by_filter_sort, select_task_by_task_id
from applications.option.options import task_executing_dic, stop_tasks_url, changePriority_url, log_url, X_forwarded_host

import math

select_task_by_user_bp = Blueprint('select_task_by_user_bp', __name__, url_prefix='/ifccd/tasks')

@select_task_by_user_bp.put('')
def select_task_by_user():
    HOST = request.headers.get("Host")
    user_name = request.values.get("user")
    if user_name is None:
        return fail_api("no user_name"), 400
    state = request.values.get("state")
    if state is None:
        return fail_api("no state"), 400
    taskType = request.values.get("taskType")
    if taskType is None:
        return fail_api("no taskType"), 400
    data = request.get_data()
    if data.decode("UTF-8") != "":
        json_data = json.loads(data.decode("UTF-8"))
        sort = json_data.get("sort")
        filter = json_data.get("filter")
    else:
        sort = None
        filter = None
    db_sort = None
    if sort is not None:
        db_sort = []
        if sort.get("sequence") is not None:
            if sort.get("sequence") == "asc":
                db_sort.append(("sequence", pymongo.ASCENDING))
            elif sort.get("sequence") == "desc":
                db_sort.append(("sequence", pymongo.DESCENDING))
        if sort.get("beginTime") is not None:
            if sort.get("beginTime") == "asc":
                db_sort.append(("create_time", pymongo.ASCENDING))
            elif sort.get("beginTime") == "desc":
                db_sort.append(("create_time", pymongo.DESCENDING))
        if sort.get("taskClassesType") is not None:
            if sort.get("taskClassesType") == "asc":
                db_sort.append(("taskClassesType", pymongo.ASCENDING))
            elif sort.get("taskClassesType") == "desc":
                db_sort.append(("taskClassesType", pymongo.DESCENDING))

    db_filter = {}
    if filter is not None:
        if filter.get("taskClassesType") is not None:
            db_filter["taskClassesType"] = filter.get("taskClassesType").get("value")
        if filter.get("beginTime") is not None:
            if filter.get('beginTime').get('operation') == "gte":
                db_filter["create_time"] = {"gte": filter.get('beginTime').get('value')}
            elif filter.get('beginTime').get('operation') == "lte":
                db_filter["create_time"] = {"lte": filter.get('beginTime').get('value')}
            elif filter.get('beginTime').get('operation') == 'range':
                db_filter["create_time"] = {"gte": filter.get('beginTime').get('value')[0], "lte": filter.get('beginTime').get('value')[1]}

    final_res_dic = {}
    res_list = [] # 函数返回的list
    results_list = [] # 存储查询数据库的结果
    if state == "1": # 完成
        db_filter["user_name"] = user_name
        db_filter["task_status"] = 1
        db_filter["task_type"] = taskType

        results = select_by_filter_sort(db_sort, db_filter)
        results_list = list(results)
        final_res_dic["total"] = results.count()

    elif state == "0": # 队列中
        if taskType == "1":
            tmpQueue = current_app.config.get("IFCCD_TASK_QUEUE").get_ifccd_task_priority_queue()
        elif taskType == "0":
            tmpQueue = current_app.config.get("ENHANCE_TASK_QUEUE").get_enhance_task_priority_queue()
        final_res_dic["total"] = len(tmpQueue)
        results_list = []
        taskid_list = []
        for i in range(len(tmpQueue)):
            taskid_list.append(tmpQueue[i].task_id)
            i = i + 1

        for tmpTaskId in taskid_list:
            results_list.append(select_task_by_task_id(tmpTaskId))





    elif state == "-1": # 未完成 正在处理
        db_filter["user_name"] = user_name
        db_filter["task_status"] = 2
        db_filter["task_type"] = taskType
        results = select_by_filter_sort(db_sort, db_filter)
        results_list = list(results)
        final_res_dic["total"] = results.count()

    else:
        return fail_api("error state"),400

    for task_dic in results_list:
        res_single_task_dic = {}
        task_id = str(task_dic.get("_id"))
        res_single_task_dic["taskId"] = task_id
        res_single_task_dic["owner"] = task_dic.get("user_name")
        if state == "1": # 完成
            res_single_task_dic["result"] = task_dic.get("task_result")
            res_single_task_dic["taskStage"] = "task_executed"
            res_single_task_dic["completeRate"] = task_dic.get("task_complete_rate")
            if res_single_task_dic["completeRate"] == 0:
                res_single_task_dic["taskStage"] = "task_error"
            res_single_task_dic["beginTime"] = task_dic.get("create_time")
            res_single_task_dic["taskClassesType"] = task_dic.get("taskClassesType")
            res_single_task_dic["taskAlgName"] = task_dic.get("task_algName")
            res_single_task_dic["currentPosInQueue"] = -1 # 位置为-1表示已经执行完毕
            res_single_task_dic["_links"] = {}
            res_single_task_dic["_links"]["log"] = {"href": X_forwarded_host + log_url + task_id}

        elif state == "0": # 队列中
            # 从全局task_executing_dic中获取当前任务状态和完成率信息
            single_task_dic = task_executing_dic.get(task_id)
            res_single_task_dic["taskStage"] = single_task_dic.get("taskStage")
            res_single_task_dic["completeRate"] = single_task_dic.get("completeRate")
            res_single_task_dic["taskAlgName"] = single_task_dic.get("task_algName")
            if task_dic.get("task_status") == 0: # 未执行
                IFCCD_TASK_QUEUE = current_app.config.get("IFCCD_TASK_QUEUE")
                ENHANCE_TASK_QUEUE = current_app.config.get("ENHANCE_TASK_QUEUE")
                ifccd_q_pos = IFCCD_TASK_QUEUE.get_pos_by_task_id(str(task_dic.get("_id")))
                enhance_q_pos = ENHANCE_TASK_QUEUE.get_pos_by_task_id(str(task_dic.get("_id")))
                if ifccd_q_pos: # 如果该任务在IFCCD_TASK_QUEUE中
                    res_single_task_dic["currentPosInQueue"] = ifccd_q_pos
                elif enhance_q_pos: # 如果该任务在ENHANCE_TASK_QUEUE中
                    res_single_task_dic["currentPosInQueue"] = enhance_q_pos
                else: # 如果该任务正在执行
                    res_single_task_dic["currentPosInQueue"] = 0
                res_single_task_dic["_links"] = {}
                res_single_task_dic["_links"]["stop"] = {"href": X_forwarded_host + stop_tasks_url + task_id}
                res_single_task_dic["_links"]["changePriority"] = {"href": X_forwarded_host + changePriority_url + task_id}
                res_single_task_dic["_links"]["log"] = {"href": X_forwarded_host + log_url + task_id}

        elif state == "-1": # 未完成
            # 从全局task_executing_dic中获取当前任务状态和完成率信息
            single_task_dic = task_executing_dic.get(task_id)
            res_single_task_dic["taskStage"] = single_task_dic.get("taskStage")
            res_single_task_dic["completeRate"] = single_task_dic.get("completeRate")
            res_single_task_dic["taskAlgName"] = single_task_dic.get("task_algName")
            res_single_task_dic["_links"] = {}
            res_single_task_dic["_links"]["log"] = {"href": X_forwarded_host + log_url + task_id}
        res_list.append(res_single_task_dic)

    rows_res_dic = {}
    rows_res_dic["rows"] = jsonify(res_list)

    final_res_dic["rows"] = res_list
    final_res_dic["_links"] = {}
    return jsonify(final_res_dic)
