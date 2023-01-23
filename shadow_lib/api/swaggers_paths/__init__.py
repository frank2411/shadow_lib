from shadow_lib.extensions import api_spec
from marshmallow import fields, Schema


class GeneralErrorSchema(Schema):
    errorfield = fields.List(fields.Str())


class GeneralMessageSchema(Schema):
    message = fields.Str()


api_spec.components.schema("GeneralErrorSchema", schema=GeneralErrorSchema)
api_spec.components.schema("GeneralMessageSchema", schema=GeneralMessageSchema)

from shadow_lib.api.swaggers_paths import auth_paths  # noqa
from shadow_lib.api.swaggers_paths import user_paths  # noqa
from shadow_lib.api.swaggers_paths import token_paths  # noqa
from shadow_lib.api.swaggers_paths import author_paths  # noqa
from shadow_lib.api.swaggers_paths import customer_paths  # noqa
from shadow_lib.api.swaggers_paths import book_paths  # noqa
from shadow_lib.api.swaggers_paths import order_paths  # noqa
from shadow_lib.api.swaggers_paths import borrowed_book_paths  # noqa
