from flask import Flask
from applications.view.ifccd.common.algs import algs_bp
from applications.view.ifccd.common.ping import ping_bp

def register_common_views(app: Flask):
    app.register_blueprint(algs_bp)
    app.register_blueprint(ping_bp)