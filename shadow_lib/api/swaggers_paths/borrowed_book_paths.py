from flask import current_app
from marshmallow import Schema, fields
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

from shadow_lib.api.resources import (
    BorrowedBookDetailResource,
    BorrowedBookListResource,
)

from shadow_lib.api.schemas import (
    BorrowedBookSingleCreationSchema,
    BorrowedBookSingleUpdateSchema,
)
from shadow_lib.models import BorrowedBook, db
from shadow_lib.extensions import api_spec


class BorrowedBookFixedSchema(SQLAlchemyAutoSchema):
    id = fields.UUID(dump_only=True)
    book_id = fields.UUID(required=True)
    order_id = fields.UUID(required=True)
    qty = fields.Int(required=True)

    class Meta:
        model = BorrowedBook
        sqla_session = db.session
        load_instance = True


class BorrowedBookSchemaRich(Schema):
    message = fields.Str()
    borrowed_book = fields.Nested(BorrowedBookFixedSchema)


class BorrowedBookSchemaMany(Schema):
    borrowed_books = fields.Nested(BorrowedBookFixedSchema(many=True))


api_spec.components.schema("BorrowedBookFixedSchema", schema=BorrowedBookFixedSchema)
api_spec.components.schema(
    "BorrowedBookSingleCreationSchema", schema=BorrowedBookSingleCreationSchema
)
api_spec.components.schema(
    "BorrowedBookSingleUpdateSchema", schema=BorrowedBookSingleUpdateSchema
)
api_spec.components.schema(
    "BorrowedBookSchemaNoMessage", schema=BorrowedBookSchemaRich(exclude=["message"])
)
api_spec.components.schema("BorrowedBookSchemaRich", schema=BorrowedBookSchemaRich)
api_spec.components.schema("BorrowedBookSchemaMany", schema=BorrowedBookSchemaMany)


api_spec.path(
    resource=BorrowedBookListResource,
    # api=api,
    app=current_app,
    operations=dict(
        get=dict(
            security=[{"bearerAuth": []}],
            summary="Returns a list of borrowed books. Only for authenticated users.",
            description="Returns a list of borrowed books. Only for authenticated users.",
            tags=["borrowed_books_list"],
            responses={
                "200": {
                    "description": "A JSON array of borrowed book objects",
                    "content": {
                        "application/json": {"schema": "BorrowedBookSchemaMany"}
                    },
                }
            },
        ),
        post=dict(
            security=[{"bearerAuth": []}],
            requestBody={
                "required": True,
                "content": {
                    "application/json": {
                        "schema": "BorrowedBookFixedSchema",
                    }
                },
            },
            summary="Creates an borrowed book",
            description="Creates an borrowed book",
            tags=["borrowed_books_list"],
            responses={
                "201": {
                    "description": "Created",
                    "content": {
                        "application/json": {"schema": "BorrowedBookSchemaRich"}
                    },
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
    resource=BorrowedBookDetailResource,
    # api=api,
    app=current_app,
    parameters=[
        {
            "name": "id",
            "in": "path",
            "required": True,
            "description": "Borrowed book id on which perfom actions.",
            "schema": {"type": "string", "format": "uuid"},
        }
    ],
    operations=dict(
        get=dict(
            security=[{"bearerAuth": []}],
            summary="Returns a borrowed book by ID, if it exists",
            description="Returns a borrowed book by ID, if it exists",
            tags=["borrowed_books_detail"],
            responses={
                "200": {
                    "description": "OK",
                    "content": {
                        "application/json": {"schema": "BorrowedBookSchemaNoMessage"}
                    },
                },
                "404": {
                    "description": "Borrowed book not found.",
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
                        "schema": "BorrowedBookSingleUpdateSchema",
                    }
                },
            },
            summary="Updates an borrowed book",
            description="Updates an borrowed book",
            tags=["borrowed_books_detail"],
            responses={
                "200": {
                    "description": "borrowed book updated",
                    "content": {
                        "application/json": {"schema": "BorrowedBookSchemaRich"}
                    },
                },
                "422": {
                    "description": "List of errors occured in update.",
                    "content": {"application/json": {"schema": "GeneralErrorSchema"}},
                },
            },
        ),
        delete=dict(
            security=[{"bearerAuth": []}],
            summary="Deletes an borrowed book",
            description="Deletes an borrowed book",
            tags=["borrowed_books_detail"],
            responses={
                "200": {
                    "description": "borrowed book deleted",
                    "content": {"application/json": {"schema": "GeneralMessageSchema"}},
                },
                "404": {
                    "description": "borrowed book not found.",
                    "content": {"application/json": {"schema": "GeneralMessageSchema"}},
                },
            },
        ),
    ),
)
