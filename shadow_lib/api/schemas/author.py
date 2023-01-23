from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from shadow_lib.models import Author, db
from marshmallow import fields
from .custom_fields import FixedRelated


class AuthorSchema(SQLAlchemyAutoSchema):

    id = fields.UUID(dump_only=True)
    created_by = FixedRelated(dump_only=True)

    class Meta:
        model = Author
        sqla_session = db.session
        load_instance = True
