from flask import current_app
from marshmallow import Schema, fields

from shadow_lib.api.resources import AuthorDetailResource, AuthorListResource

from shadow_lib.api.schemas import AuthorSchema
from shadow_lib.extensions import api_spec


class AuthorSchemaRich(Schema):
    message = fields.Str()
    author = fields.Nested(AuthorSchema)


class AuthorSchemaMany(Schema):
    authors = fields.Nested(AuthorSchema(many=True))


api_spec.components.schema("AuthorSchema", schema=AuthorSchema)
api_spec.components.schema(
    "AuthorSchemaNoMessage", schema=AuthorSchemaRich(exclude=["message"])
)
api_spec.components.schema("AuthorSchemaRich", schema=AuthorSchemaRich)
api_spec.components.schema("AuthorSchemaMany", schema=AuthorSchemaMany)


api_spec.path(
    resource=AuthorListResource,
    # api=api,
    app=current_app,
    operations=dict(
        get=dict(
            security=[{"bearerAuth": []}],
            summary="Returns a list of authors. Only for authenticated users.",
            description="Returns a list of authors. Only for authenticated users.",
            tags=["authors_list"],
            responses={
                "200": {
                    "description": "A JSON array of author objects",
                    "content": {"application/json": {"schema": "AuthorSchemaMany"}},
                }
            },
        ),
        post=dict(
            security=[{"bearerAuth": []}],
            requestBody={
                "required": True,
                "content": {
                    "application/json": {
                        "schema": "AuthorSchema",
                    }
                },
            },
            summary="Creates an author",
            description="Creates an author",
            tags=["authors_list"],
            responses={
                "201": {
                    "description": "Created",
                    "content": {"application/json": {"schema": "AuthorSchemaRich"}},
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
    resource=AuthorDetailResource,
    # api=api,
    app=current_app,
    parameters=[
        {
            "name": "id",
            "in": "path",
            "required": True,
            "description": "Author id on which perfom actions.",
            "schema": {"type": "string", "format": "uuid"},
        }
    ],
    operations=dict(
        get=dict(
            security=[{"bearerAuth": []}],
            summary="Returns an author by ID, if it exists",
            description="Returns an author by ID, if it exists",
            tags=["authors_detail"],
            responses={
                "200": {
                    "description": "OK",
                    "content": {
                        "application/json": {"schema": "AuthorSchemaNoMessage"}
                    },
                },
                "404": {
                    "description": "author not found.",
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
                        "schema": "AuthorSchema",
                    }
                },
            },
            summary="Updates an author",
            description="Updates an author",
            tags=["authors_detail"],
            responses={
                "200": {
                    "description": "author updated",
                    "content": {"application/json": {"schema": "AuthorSchemaRich"}},
                },
                "422": {
                    "description": "List of errors occured in update.",
                    "content": {"application/json": {"schema": "GeneralErrorSchema"}},
                },
            },
        ),
        delete=dict(
            security=[{"bearerAuth": []}],
            summary="Deletes an author",
            description="Deletes an author",
            tags=["authors_detail"],
            responses={
                "200": {
                    "description": "Author deleted",
                    "content": {"application/json": {"schema": "GeneralMessageSchema"}},
                },
                "404": {
                    "description": "Author not found.",
                    "content": {"application/json": {"schema": "GeneralMessageSchema"}},
                },
            },
        ),
    ),
)
