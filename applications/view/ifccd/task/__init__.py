from flask import Flask
from applications.view.ifccd.task.create_ifccd_task import create_ifccd_task_bp
from applications.view.ifccd.task.create_enhance_task import create_enhance_task_bp
from applications.view.ifccd.task.select_logs_by_taskId import select_logs_by_taskid_bp
from applications.view.ifccd.task.stop_task import stop_task_bp
from applications.view.ifccd.task.select_tasks_by_user import select_task_by_user_bp
from applications.view.ifccd.task.logical_delete import logical_delete_bp
def register_task_views(app: Flask):
    app.register_blueprint(create_ifccd_task_bp)
    app.register_blueprint(create_enhance_task_bp)
    app.register_blueprint(stop_task_bp)
    app.register_blueprint(select_task_by_user_bp)
    app.register_blueprint(select_logs_by_taskid_bp)
    app.register_blueprint(logical_delete_bp)