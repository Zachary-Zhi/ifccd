import datetime
import json
from datetime import timezone
from datetime import timedelta

SHA_TZ = timezone(
    timedelta(hours=8),
    name='Asia/Shanghai'
)
#
class Task(object):
    def __init__(self, task_params_json, task_status, task_type, taskClassesType, user_name = "", task_description = "", task_algName = ""):
        self.user_name = user_name
        self.task_description = task_description
        self.task_params_json = task_params_json
        self.task_status = task_status  # 0 未执行  1 已执行 2 正在处理 3 已停止 5 因错误停止
        self.create_time = str(datetime.datetime.now().astimezone(SHA_TZ))
        self.task_type = task_type  # 0 短任务 1 长任务
        self.taskClassesType = taskClassesType  # 表示子任务类型
        self.task_id = None
        self.end_time = None
        self.task_algName = task_algName


    def class_to_json(self):
        return json.dumps(self, default=lambda self: self.__dict__, sort_keys=True, indent=4)


    def json_to_dic(self, task_json):
        return json.loads(task_json)

