from applications.extensions import ma
from marshmallow import fields


class TaskOutSchema(ma.Schema):
    task_id = fields.Integer()
    user_name = fields.Str()
    task_description = fields.Str()
    create_time = fields.DateTime()
    task_params_json = fields.Str()
    task_status = fields.Integer()