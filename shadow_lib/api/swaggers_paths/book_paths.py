from flask import current_app
from marshmallow import Schema, fields

from shadow_lib.api.resources import (
    BookDetailResource,
    BookListResource,
    BookSearchResource,
)

from shadow_lib.api.schemas import BookSchema
from shadow_lib.extensions import api_spec


class BookSchemaRich(Schema):
    message = fields.Str()
    book = fields.Nested(BookSchema)


class BookSchemaMany(Schema):
    books = fields.Nested(BookSchema(many=True))


api_spec.components.schema("BookSchema", schema=BookSchema)
api_spec.components.schema(
    "BookSchemaNoMessage", schema=BookSchemaRich(exclude=["message"])
)
api_spec.components.schema("BookSchemaRich", schema=BookSchemaRich)
api_spec.components.schema("BookSchemaMany", schema=BookSchemaMany)


api_spec.path(
    resource=BookListResource,
    # api=api,
    app=current_app,
    operations=dict(
        get=dict(
            security=[{"bearerAuth": []}],
            summary="Returns a list of books. Only for authenticated users.",
            description="Returns a list of books. Only for authenticated users.",
            tags=["books_list"],
            responses={
                "200": {
                    "description": "A JSON array of book objects",
                    "content": {"application/json": {"schema": "BookSchemaMany"}},
                }
            },
        ),
        post=dict(
            security=[{"bearerAuth": []}],
            requestBody={
                "required": True,
                "content": {
                    "application/json": {
                        "schema": "BookSchema",
                    }
                },
            },
            summary="Creates a book",
            description="Creates a book",
            tags=["books_list"],
            responses={
                "201": {
                    "description": "Created",
                    "content": {"application/json": {"schema": "BookSchemaRich"}},
                },
                "422": {
                    "description": "List of errors occured in creation.",
                    "content": {"application/json": {"schema": "GeneralErrorSchema"}},
                },
            },
        ),
    ),
)


# OrganizationDetailResource
api_spec.path(
    resource=BookDetailResource,
    # api=api,
    app=current_app,
    parameters=[
        {
            "name": "id",
            "in": "path",
            "required": True,
            "description": "Book id on which perfom actions.",
            "schema": {"type": "string", "format": "uuid"},
        }
    ],
    operations=dict(
        get=dict(
            security=[{"bearerAuth": []}],
            summary="Returns a book by ID, if it exists",
            description="Returns a book by ID, if it exists",
            tags=["books_detail"],
            responses={
                "200": {
                    "description": "OK",
                    "content": {"application/json": {"schema": "BookSchemaNoMessage"}},
                },
                "404": {
                    "description": "book not found.",
                    "content": {"application/json": {"schema": "GeneralMessageSchema"}},
                },
            },
        ),
        patch=dict(
            security=[{"bearerAuth": []}],
            requestBody={
                "required": True,
                "content": {
                    "application/json": {
                        "schema": "BookSchema",
                    }
                },
            },
            summary="Updates a book",
            description="Updates a book",
            tags=["books_detail"],
            responses={
                "200": {
                    "description": "book updated",
                    "content": {"application/json": {"schema": "BookSchemaRich"}},
                },
                "422": {
                    "description": "List of errors occured in update.",
                    "content": {"application/json": {"schema": "GeneralErrorSchema"}},
                },
            },
        ),
        delete=dict(
            security=[{"bearerAuth": []}],
            summary="Deletes a book",
            description="Deletes a book",
            tags=["books_detail"],
            responses={
                "200": {
                    "description": "book deleted",
                    "content": {"application/json": {"schema": "GeneralMessageSchema"}},
                },
                "404": {
                    "description": "book not found.",
                    "content": {"application/json": {"schema": "GeneralMessageSchema"}},
                },
            },
        ),
    ),
)


# OrganizationDetailResource
api_spec.path(
    resource=BookSearchResource,
    # api=api,
    app=current_app,
    parameters=[
        {
            "name": "q",
            "in": "query",
            "required": True,
            "description": (
                "Generic query parameter. Searches in Book.title, Book.EAN, "
                "Book.SKU, Author.first_name, Author.last_name"
            ),
            "schema": {"type": "string"},
        }
    ],
    operations=dict(
        get=dict(
            security=[{"bearerAuth": []}],
            summary="Returns a book by ID, if it exists",
            description="Returns a book by ID, if it exists",
            tags=["books_search"],
            responses={
                "200": {
                    "description": "A JSON array of book objects",
                    "content": {"application/json": {"schema": "BookSchemaMany"}},
                },
                "422": {
                    "description": "List of errors occured in search.",
                    "content": {"application/json": {"schema": "GeneralErrorSchema"}},
                },
            },
        ),
    ),
)
