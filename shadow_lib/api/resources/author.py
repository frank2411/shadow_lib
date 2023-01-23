import uuid

from flask import current_app, g, request
from flask_restful import Resource
from marshmallow import ValidationError

from shadow_lib.decorators import authenticate_user, check_bearer_token


from shadow_lib.custom_types import ErrorResponseType, SuccessResponseType
from shadow_lib.models import Author
from shadow_lib.api.schemas import AuthorSchema


class AuthorDetailResource(Resource):

    method_decorators = [
        authenticate_user,
        check_bearer_token,
    ]

    def get(self, author_id: uuid.UUID) -> SuccessResponseType:
        schema = AuthorSchema()
        author = Author.get_author(author_id, g.current_user)
        return {"author": schema.dump(author)}

    def patch(self, author_id: uuid.UUID) -> SuccessResponseType | ErrorResponseType:
        author = Author.get_author(author_id, g.current_user)
        schema = AuthorSchema(partial=True, instance=author)

        try:
            author = schema.load(request.json)
        except ValidationError as err:
            return err.messages, 422

        author.save()
        return {"message": "author updated", "author": schema.dump(author)}

    def delete(self, author_id: uuid.UUID) -> SuccessResponseType:
        author = Author.get_author(author_id, g.current_user)
        author.delete()
        current_app.logger.info(f"author {author.id} deleted")
        return {"message": "author deleted"}


class AuthorListResource(Resource):
    """Creation and get_all"""

    method_decorators = [
        authenticate_user,
        check_bearer_token,
    ]

    def get(self) -> SuccessResponseType:
        schema = AuthorSchema(many=True)
        authors = Author.get_authors(g.current_user)
        return {"authors": schema.dump(authors)}

    def post(self) -> SuccessResponseType | ErrorResponseType:
        try:
            schema = AuthorSchema()
            author: Author = schema.load(request.json)
        except ValidationError as err:
            return err.messages, 422

        author.created_by_id = g.current_user.id
        author.save()

        current_app.logger.info(f"author {author.id} created")

        return {
            "message": "author created",
            "author": schema.dump(author),
        }, 201
