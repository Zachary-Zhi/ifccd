from flask import current_app

from applications import create_app
from flask_migrate import Migrate
from applications.common.utils.task_priority_queues import ifccd_task_priority_queue, enhance_task_priority_queue
from applications.common.utils.myThread import init_task_handle_thread
from applications.extensions.init_pymongo import db
from applications.reposity.task_reposity import select_tasks_by_task_status, update_task_status_by_task_id

app = create_app()
migrate = Migrate(app, db)

with app.app_context():
    # 任务优先队列
    IFCCD_TASK_QUEUE = ifccd_task_priority_queue()
    current_app.config["IFCCD_TASK_QUEUE"] = IFCCD_TASK_QUEUE
    ENHANCE_TASK_QUEUE = enhance_task_priority_queue()
    current_app.config["ENHANCE_TASK_QUEUE"] = ENHANCE_TASK_QUEUE
    current_app.config["task_executing_dic"] = {}
    init_task_handle_thread()
    tasks_dic = select_tasks_by_task_status(0)
    for t_tasks in tasks_dic:
        update_task_status_by_task_id(t_tasks.get("_id"), 5)
    tasks_dic = select_tasks_by_task_status(2)
    for t_tasks in tasks_dic:
        update_task_status_by_task_id(t_tasks.get("_id"), 5)


@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'


if __name__ == '__main__':
    app.run()
