import logging
import os
import queue
from collections import deque
from bson.objectid import ObjectId
id = ObjectId("64258dd4fc136616b4bf2c9a")
print(id)
print(type(id))
print(id.generation_time)
print(str(id))

a_dic = {}
a_dic["1"] = {"id":1, "taskStage":"preprocess", "completeRate":20, "result":"xxxx/xxxx/x"}
a_dic["2"] = {"id":2, "taskStage":"preprocess", "completeRate":20, "result":"xxxx/xxxx/x"}
a_dic["3"] = {"id":3, "taskStage":"preprocess", "completeRate":20, "result":"xxxx/xxxx/x"}
a_dic["4"] = {"id":4, "taskStage":"preprocess", "completeRate":20, "result":"xxxx/xxxx/x"}
print(a_dic)
a_dic.pop("1")
print(a_dic)
a_dic["2"]["completeRate"] = 40
print(a_dic)
print(a_dic.get("3"))
print(a_dic.get("100") == None)


dq = deque()
dq.append(1)
dq.append(2)
dq.append(3)
dq.popleft()
dq.popleft()
dq.popleft()
dq.popleft()
