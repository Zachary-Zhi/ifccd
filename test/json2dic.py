from datetime import datetime

import pymongo
from bson import ObjectId
from flask import jsonify
import os


client = pymongo.MongoClient(host='127.0.0.1')

db = client.ifccd

coll = db.task

# class Task1(object):
#     def __init__(self, user_name, task_params_json, task_status):
#         self.user_name = user_name
#         self.task_params_json = task_params_json
#         self.task_status = task_status
#

# coll.insert(jsonify(task))
task = coll.find_one({"_id": ObjectId("64112a8ffc13664cc0ee3b31") })
print(task)
print(type(task))
task_params_dic = task.get("task_params_json")

m_operator = task_params_dic.get("action")
photo_import_path = "..\\static\\photo\\"
photo_import_name = "img_001.png";
# photo_output_path = task_params_dic.get("output")
photo_output_path = ""
alg_dic = ""
# if "adjust" == m_operator:
#     process_adjust_task(alg_dic, photo_import_path, photo_output_path)
# elif "denoise" == m_operator:
#     process_denoise_task(alg_dic, photo_import_path, photo_output_path)
# elif "enhance" == m_operator:
#     process_denoise_task(alg_dic, photo_import_path, photo_output_path)
# elif "revise" == m_operator:
#     process_revise_task(alg_dic, photo_import_path, photo_output_path)
# else:
#     print("unknown action")


def process_adjust_task(alg_dic, photo_import_path, photo_import_name, photo_output_path):
    src_file = open(photo_import_path+photo_import_name, "rb")
    split_for_pin = photo_import_name.split(".")
    photo_output_name = split_for_pin[0] + "_adjust." + split_for_pin[1]
    target_file = open(photo_import_path+photo_output_name, "wb")
    target_file.write(src_file.read())
    target_file.close()
    src_file.close()

process_adjust_task(alg_dic, photo_import_path, photo_import_name, photo_output_path)








client.close()