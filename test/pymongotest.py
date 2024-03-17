from datetime import datetime

import pymongo
from flask import jsonify

client = pymongo.MongoClient(host='127.0.0.1')

db = client.ifccd

coll = db.task


# class Task(db.Document):
#     task_id = db.IntField()
#     user_name = db.StringField()
#     task_description = db.StringField()
#     create_time = db.DateTimeField(default=datetime.datetime.now())
#     task_params_json = db.StringField()
#     task_status = db.IntField()  # 0 未执行  1 已执行 2 正在处理
#     end_time = 	db.DateTimeField()
#

class Task1(object):
    def __init__(self, user_name, task_params_json, task_status):
        self.user_name = user_name
        self.task_params_json = task_params_json
        self.task_status = task_status

# task = Task(user_name="zhangsan", task_params_json="{name:zhangsan, age:10}", task_status=0)
# print(jsonify(task))
task1 = Task1("zhangsan", "{name:zhangsan, age:10}", 0)
print(jsonify(task1))

# coll.insert(jsonify(task))




client.close()