from typing import Any
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow import post_load, ValidationError

# from marshmallow import post_load, pre_load, ValidationError, validates

# from marshmallow import
from marshmallow.fields import UUID, Int

from shadow_lib.models import db, BorrowedBook
from .custom_fields import FixedRelated


class BorrowedBookSingleUpdateSchema(SQLAlchemyAutoSchema):

    error_messages = {
        "qty_exceeded": "Quantity for this book {book_id} is too much",
    }

    id = UUID(dump_only=True)
    order = FixedRelated(data_key="order_id", required=True)
    book = FixedRelated(data_key="book_id", required=True, dump_only=True)

    def reset_qty(self, data: dict):
        # I in every case, reset the quantity without persisting it in the db
        self.instance.book.qty += self.instance.qty

    @post_load
    def check_and_update_qty(self, data: dict, **kwargs: Any):
        if not data.get("qty"):
            return data

        self.reset_qty(data)

        if self.instance.book.qty < data["qty"]:
            raise ValidationError(
                self.error_messages["qty_exceeded"].format(
                    book_id=self.instance.book_id
                ),
                "book",
            )

        self.instance.book.qty -= data["qty"]
        self.instance.book.save()

        return data

    class Meta:
        model = BorrowedBook
        sqla_session = db.session
        load_instance = True


class BorrowedBookSingleCreationSchema(SQLAlchemyAutoSchema):

    error_messages = {
        "qty_exceeded": "Quantity for this book {book_id} is too much",
    }

    id = UUID(dump_only=True)
    order = FixedRelated(data_key="order_id", required=True)
    book = FixedRelated(data_key="book_id", required=True)
    qty = Int(required=True)

    @post_load
    def check_and_update_qty(self, data: dict, **kwargs: Any):
        if data["book"].qty < data["qty"]:
            raise ValidationError(
                self.error_messages["qty_exceeded"].format(book_id=data["book"].id),
                "book",
            )

        # No problems I can go further and update qty
        book = data["book"]
        book.qty -= data["qty"]
        book.save()
        return data

    class Meta:
        model = BorrowedBook
        sqla_session = db.session
        load_instance = True
