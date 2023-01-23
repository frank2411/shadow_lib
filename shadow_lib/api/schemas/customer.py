from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow_sqlalchemy.fields import RelatedList

from shadow_lib.models import Customer, db
from .custom_fields import FixedRelated
from marshmallow import fields


class CustomerSchema(SQLAlchemyAutoSchema):
    id = fields.UUID(dump_only=True)

    orders = RelatedList(FixedRelated(), dump_only=True)
    created_by = FixedRelated(dump_only=True)

    class Meta:
        model = Customer
        sqla_session = db.session
        load_instance = True
