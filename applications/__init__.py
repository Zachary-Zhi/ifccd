import os
from flask import Flask

from applications.view import init_view
from applications.configs import config


def create_app(config_name=None):
    app = Flask(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

    if not config_name:
        # 尝试从本地环境中读取
        config_name = os.getenv('FLASK_CONFIG', 'development')

    # 引入数据库配置
    app.config.from_object(config[config_name])

    # 注册路由
    init_view(app)

    return app

