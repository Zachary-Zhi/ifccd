from enum import Enum

# 对应mongodb中task_status字段值的含义，因为enum类型无法进行json转换。实际没有作用
class task_status_enum(Enum):
    task_unexecute = 0  # 未执行
    task_executed = 1    # 已执行
    task_executing = 2  # 正在处理
    task_stoped = 3     # 已停止
    task_error_stoped = 5  # 5 出错停止
    task_logical_delete = 6
