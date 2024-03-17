import datetime

from bson.objectid import ObjectId
from applications.option import options
from applications.extensions.init_pymongo import db
from applications.option.options import page_size
from datetime import timezone
from datetime import timedelta

SHA_TZ = timezone(
    timedelta(hours=8),
    name='Asia/Shanghai'
)

task_coll = db['task']



# 返回值为task_id 即为 _id
def insert_task(task_dic):
    result = task_coll.insert(task_dic)
    print(result)
    return result

# 返回值为dic集合，可以通过 for in 来遍历
def select_tasks_by_username(username):
    return task_coll.find({"user_name": username})

def select_tasks_by_username_and_status(username, status):
    return task_coll.find({"user_name": username, "task_status": status})

def select_tasks_by_status(status):
    return task_coll.find({"task_status": status})

def select_tasks_by_username_and_status_taskType(username, status, taskType, PagingNum_str, sort, filter):
    mongdb_sort = []

    return task_coll.find({"user_name": username, "task_status": status, "task_type":taskType})

def select_logs_by_task_id(task_id):
    return task_coll.find({"_id": ObjectId(task_id)})  # @@@

def select_by_filter_sort_paging(db_sort, db_filter, PagingNum):
    skipNum = page_size * (PagingNum - 1)
    print(db_sort)
    print(db_filter)
    if db_sort is None:
        return task_coll.find(db_filter).limit(page_size).skip(skipNum)
    else:
        return task_coll.find(db_filter).sort(db_sort).limit(page_size).skip(skipNum)

def select_by_filter_sort(db_sort, db_filter):
    print(db_sort)
    print(db_filter)
    if db_sort is None:
        return task_coll.find(db_filter)
    else:
        return task_coll.find(db_filter).sort(db_sort)

def select_num_by_filter_sort(db_sort, db_filter):
    print(db_sort)
    print(db_filter)
    if db_sort is None:
        return task_coll.find(db_filter).count()
    else:
        return task_coll.find(db_filter).sort(db_sort).count()
    

# 返回值为对应task的dic
def select_task_by_task_id(task_id):
    return task_coll.find_one({"_id": ObjectId(task_id) })

def select_tasks_by_task_status(status):
    return task_coll.find({"task_status":status})

def update_task_status_by_task_id(task_id, status):
    task_coll.update_one({"_id": ObjectId(task_id)}, {"$set": {"task_status": status}})

def update_task_completeRate_by_task_id(task_id, completeRate):
    task_coll.update_one({"_id": ObjectId(task_id)}, {"$set": {"task_complete_rate": completeRate}})


def update_task_logs_by_task_id(task_id, logs):
    task_coll.update_one({"_id": ObjectId(task_id)}, {"$set": {"logs": logs}}) #存日志

def update_task_resulturl_by_task_id(task_id, resulturl):
    task_coll.update_one({"_id": ObjectId(task_id)}, {"$set": {"task_result": resulturl}})

def update_task_endtime_by_task_id(task_id):
    task_coll.update_one({"_id": ObjectId(task_id)}, {"$set": {"end_time": str(datetime.datetime.now().astimezone(SHA_TZ))}})

def update_task_classes_type_by_taskid(task_id, taskClassesType):
    task_coll.update_one({"_id": ObjectId(task_id)}, {"$set": {"task_classes_type": taskClassesType}})
