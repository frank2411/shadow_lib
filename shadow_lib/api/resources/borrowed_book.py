import uuid

from flask import current_app, g, request
from flask_restful import Resource
from marshmallow import ValidationError

from shadow_lib.decorators import authenticate_user, check_bearer_token


from shadow_lib.custom_types import ErrorResponseType, SuccessResponseType
from shadow_lib.models import BorrowedBook
from shadow_lib.api.schemas import (
    BorrowedBookSingleUpdateSchema,
    BorrowedBookSingleCreationSchema,
)


class BorrowedBookDetailResource(Resource):

    method_decorators = [
        authenticate_user,
        check_bearer_token,
    ]

    def get(self, borrowed_book_id: uuid.UUID) -> SuccessResponseType:
        schema = BorrowedBookSingleUpdateSchema()
        br_book = BorrowedBook.get_borrowed_book(borrowed_book_id, g.current_user)
        return {"borrowed_book": schema.dump(br_book)}

    def patch(
        self, borrowed_book_id: uuid.UUID
    ) -> SuccessResponseType | ErrorResponseType:
        br_book = BorrowedBook.get_borrowed_book(borrowed_book_id, g.current_user)
        schema = BorrowedBookSingleUpdateSchema(partial=True, instance=br_book)

        try:
            br_book = schema.load(request.json)
        except ValidationError as err:
            return err.messages, 422

        br_book.save()
        return {
            "message": "borrowed book updated",
            "borrowed_book": schema.dump(br_book),
        }

    def delete(self, borrowed_book_id: uuid.UUID) -> SuccessResponseType:
        br_book = BorrowedBook.get_borrowed_book(borrowed_book_id, g.current_user)
        br_book.delete()

        # Reset related book quantity
        br_book.book.qty += br_book.qty
        br_book.save()

        current_app.logger.info(f"borrowed book {br_book.id} deleted")
        return {"message": "borrowed book deleted"}


class BorrowedBookListResource(Resource):
    """Creation and get_all"""

    method_decorators = [
        authenticate_user,
        check_bearer_token,
    ]

    def get(self) -> SuccessResponseType:
        schema = BorrowedBookSingleUpdateSchema(many=True)
        br_books = BorrowedBook.get_borrowed_books(g.current_user)
        return {"borrowed_books": schema.dump(br_books)}

    def post(self) -> SuccessResponseType | ErrorResponseType:
        try:
            schema = BorrowedBookSingleCreationSchema()
            br_book: BorrowedBook = schema.load(request.json)
        except ValidationError as err:
            return err.messages, 422

        # br_book.created_by_id = g.current_user.id
        br_book.save()

        current_app.logger.info(f"borrowed book {br_book.id} created")

        return {
            "message": "borrowed book created",
            "borrowed_book": schema.dump(br_book),
        }, 201
