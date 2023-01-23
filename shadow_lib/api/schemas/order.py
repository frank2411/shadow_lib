from typing import Any
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow_sqlalchemy.fields import Nested
from marshmallow import post_load, pre_load, ValidationError, validates

# from marshmallow import
# from marshmallow.fields import UUID

from shadow_lib.models import Order, db, BorrowedBook
from .custom_fields import FixedRelated


class BorrowedBookSchema(SQLAlchemyAutoSchema):

    error_messages = {
        "qty_exceeded": "Quantity for this book {book_id} is too much",
    }

    order = FixedRelated(dump_only=True, data_key="order_id")
    book = FixedRelated(required=True, data_key="book_id")

    @post_load
    def check_and_update_qty(self, instance: BorrowedBook, **kwargs: Any):
        if instance["book"].qty < instance["qty"]:
            raise ValidationError(
                self.error_messages["qty_exceeded"].format(book_id=instance["book"].id),
                "book",
            )

        # No problems I can go further and update qty
        book = instance["book"]
        book.qty -= instance["qty"]
        book.save()

        return instance

    class Meta:
        model = BorrowedBook
        sqla_session = db.session
        load_instance = True


class OrderSchema(SQLAlchemyAutoSchema):

    borrowed_books = Nested(BorrowedBookSchema, many=True, required=True)
    customer = FixedRelated(required=True)
    created_by = FixedRelated(dump_only=True)

    @validates("borrowed_books")
    def validate_groups_empty_list(self, value: list) -> None:
        if value == []:
            raise ValidationError("Borrowed book value cannot be empty.")

    @pre_load
    def set_original_qty(self, data: dict, *args, **kwargs: Any):
        if self.instance:
            self.context["parent"] = self.instance
        return data

    class Meta:
        model = Order
        sqla_session = db.session
        load_instance = True
