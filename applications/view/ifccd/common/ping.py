from flask import Blueprint
from applications.common.utils.http import success_api
import os

ping_bp = Blueprint('ping', __name__, url_prefix='/ifccd/ping')

@ping_bp.get('')
def ping():
    return success_api("pong")

