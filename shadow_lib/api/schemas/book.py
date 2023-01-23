from marshmallow import validates, ValidationError

from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow_sqlalchemy.fields import RelatedList
from marshmallow import fields

from shadow_lib.models import Book, db
from .custom_fields import FixedRelated


class BookSchema(SQLAlchemyAutoSchema):

    id = fields.UUID(dump_only=True)

    authors = RelatedList(
        FixedRelated(),
        required=True,
    )
    created_by = FixedRelated(dump_only=True)

    @validates("authors")
    def validate_groups_empty_list(self, value: list) -> None:
        if value == []:
            raise ValidationError("Authors value cannot be empty.")

    class Meta:
        model = Book
        sqla_session = db.session
        load_instance = True
