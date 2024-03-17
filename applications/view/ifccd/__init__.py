from applications.view.ifccd.config import register_config_view
from applications.view.ifccd.common import register_common_views
from applications.view.ifccd.task import register_task_views
from applications.view.ifccd.priority import register_change_priority_view

def init_ifccd_view(app):
    register_config_view(app)
    register_common_views(app)
    register_task_views(app)
    register_change_priority_view(app)