from flask import current_app
from marshmallow import Schema, fields, validate

from shadow_lib.api.resources import Login
from shadow_lib.extensions import api_spec


class LoginSchema(Schema):
    email = fields.Str(required=True, validate=validate.Email())
    password = fields.Str(required=True)


class LoginResponseSchema(Schema):
    access_token = fields.Str(required=True, validate=validate.Email())
    refresh_token = fields.Str(required=True)


api_spec.components.schema("LoginSchema", schema=LoginSchema)
api_spec.components.schema("LoginResponseSchema", schema=LoginResponseSchema)


# OrganizationListResource
api_spec.path(
    resource=Login,
    # api=api,
    app=current_app,
    operations=dict(
        post=dict(
            requestBody={
                "required": True,
                "content": {
                    "application/json": {
                        "schema": "LoginSchema",
                    }
                },
            },
            summary="Authenticate user.",
            description="Returns access and refresh token if successful.",
            tags=["auth"],
            responses={
                "200": {
                    "description": "Login successful.",
                    "content": {"application/json": {"schema": "LoginResponseSchema"}},
                },
                "400": {
                    "description": "Error. Bad credentials.",
                    "content": {"application/json": {"schema": "GeneralMessageSchema"}},
                },
            },
        )
    ),
)
