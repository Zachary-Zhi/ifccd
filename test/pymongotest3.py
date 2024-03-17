import datetime
from bson.objectid import ObjectId
import pymongo
import pprint
import json
import re

# from flask import Flask, request
# from flask_mongoalchemy import MongoAlchemy, BaseQuery
#
# app = Flask(__name__)
# app.config['DEBUG'] = True
# app.config['MONGOALCHEMY_DATABASE'] = 'ifccd'
# db = MongoAlchemy(app)


# from applications.models import Task

client = pymongo.MongoClient(host='192.168.8.166')

db = client.ifccd

# db = client.ifccd
task_collections = db.task

# tasks_dic = task_collections.find({"user_name":"zhangsan"})
# # for tmp_task in tasks_dic:
# #     print(tmp_task)
# print("=======================================")
# page_size = 5
# page_no = 2
# skip = page_size * (page_no - 1)
# tasks_dic = task_collections.find({"user_name":"zhangsan"}).limit(5).skip(skip)
# for tmp_task in tasks_dic:
#     print(tmp_task)
# print("======================")
# # res = task_collections.find().sort("create_time", pymongo.DESCENDING)
# #
# # for tmp_task in res:
# #     print(tmp_task)
#
# # res = task_collections.find({"user_name":"zhangsan", "create_time": {"$lt":"2023-04-12 16:51:28.154279"}})
# res = task_collections.find({"user_name":"zhangsan", "create_time": {"$lt":"2023-04-12 16:51:28.154279"}})
# for tmp_task in res:
#     print(tmp_task)
#
# print("===============")
# query_condition = {'taskClassesType': 'adjust', 'user_name': 'zhangsan', 'task_status': 1, 'task_type': '0'}


query_condition = {}
# sort_condition = [("create_time", pymongo.DESCENDING), ("task_status", pymongo.DESCENDING)]
sort_condition= [('create_time', -1)]

res = task_collections.find(query_condition).sort(sort_condition)

## 注意上面函数执行之后会导致count有结果，但是输出没结果
# print(res)
# print(res.count())
# print(type(res.count()))
# print(len(list(res)))
# print(type(len(list(res))))
resList = list(res)
print(len(resList))
# print(resList.count())
for tmp_task in resList:
    print(tmp_task)



print(int("3") *10)
print(resList)




