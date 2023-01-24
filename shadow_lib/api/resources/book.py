import uuid

from flask import current_app, g, request
from flask_restful import Resource
from marshmallow import ValidationError

from shadow_lib.decorators import authenticate_user, check_bearer_token


from shadow_lib.custom_types import ErrorResponseType, SuccessResponseType
from shadow_lib.models import Book

from shadow_lib.api.schemas import BookSchema, BookSearchSchema


class BookDetailResource(Resource):

    method_decorators = [
        authenticate_user,
        check_bearer_token,
    ]

    def get(self, book_id: uuid.UUID) -> SuccessResponseType:
        schema = BookSchema()
        book = Book.get_book(book_id, g.current_user)
        return {"book": schema.dump(book)}

    def patch(self, book_id: uuid.UUID) -> SuccessResponseType | ErrorResponseType:
        book = Book.get_book(book_id, g.current_user)
        schema = BookSchema(partial=True, instance=book)

        try:
            book = schema.load(request.json)
        except ValidationError as err:
            return err.messages, 422

        book.save()
        return {"message": "book updated", "book": schema.dump(book)}

    def delete(self, book_id: uuid.UUID) -> SuccessResponseType:
        book = Book.get_book(book_id, g.current_user)
        book.delete()
        current_app.logger.info(f"book {book.id} deleted")
        return {"message": "book deleted"}


class BookListResource(Resource):
    """Creation and get_all"""

    method_decorators = [
        authenticate_user,
        check_bearer_token,
    ]

    def get(self) -> SuccessResponseType:
        schema = BookSchema(many=True)
        books = Book.get_books(g.current_user)
        return {"books": schema.dump(books)}

    def post(self) -> SuccessResponseType | ErrorResponseType:
        try:
            schema = BookSchema()
            book: Book = schema.load(request.json)
        except ValidationError as err:
            return err.messages, 422

        book.created_by_id = g.current_user.id
        book.save()

        current_app.logger.info(f"book {book.id} created")

        return {
            "message": "book created",
            "book": schema.dump(book),
        }, 201


class BookSearchResource(Resource):
    """Creation and get_all"""

    method_decorators = [
        authenticate_user,
        check_bearer_token,
    ]

    def get(self) -> SuccessResponseType:
        try:
            validated_filters = BookSearchSchema()
            validated_filters = validated_filters.load(request.args)
        except ValidationError as err:
            return err.messages, 422

        schema = BookSchema(many=True)
        books = Book.search_books(g.current_user, validated_filters)
        return {"books": schema.dump(books)}
