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

client = pymongo.MongoClient(host='127.0.0.1')

db = client.ifccd
# print(db)
#
# db_list = client.database_names()
# print(db_list)
#
# collections = db.stus
# result = collections.insert_one({
#     'name':"tom",
#     'age':3,
# })
# print(result)
# print(result.inserted_id)

class Book(object):
    def __init__(self, title, author, year):
        self.title = title
        self.author = author
        self.year = year


# db = client.ifccd
task_collections = db.book
# task1 = Task(user_name="zhangsan", task_description="", create_time=datetime.datetime.now(),
#              task_params_json={'username': 'zhangsan'}, task_status=0)
book = Book("english", "jerry", 2022)
print(book)

str = json.dumps(book, default=lambda book: book.__dict__, sort_keys=True, indent=4)
print(str)
print(type(str))

dict_str = json.loads(str)
print(dict_str)
print(type(dict_str))
# task_collections.insert_one(dict_str)
# result = task_collections.insert_one()

# print(result.inserted_id)
# result = task_collections.insert({"title":"math", "author":"tom", "year":2012})
# print(result)
# print(result.title)
result1 = task_collections.find_one({"title":"math"})
print("result1: ", result1, "\tresult1 type: " , type(result1))
print("---------------------------------")
# pprint.pprint(task_collections.find_one({"title":"math"}))

result2 = task_collections.find({"author":"tom"})
print(result2)
print(type(result2))
for ite in result2:
    pprint.pprint(ite)
    print(type(ite))



# web framework从URl中获取post_id并将其转为string
document = task_collections.find_one({"_id": ObjectId("640fe0d3fc136637206249d2")})
print(document)


result3 = task_collections.update_one({"_id":ObjectId("640fe0d3fc136637206249d2")}, {"$set":{"end_time":datetime.datetime.now()}})
print(result3)
# result3 = task_collections.update_one({"_id":ObjectId("640fe0d3fc136637206249d2")}, {"$set":{"title":"math2"}})

