from applications.extensions import ma
from marshmallow import fields


class PhotoOutSchema(ma.Schema):
    photo_id = fields.Integer()
    photo_name = fields.Str()
    nas_url = fields.Str()
    mime = fields.Str()
    size = fields.Str()
    create_time = fields.DateTime()
    task_id = fields.Integer()
    type = fields.Integer()
