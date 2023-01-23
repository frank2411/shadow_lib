from flask import current_app
from marshmallow import Schema, fields

from shadow_lib.api.resources import RefreshToken, RevokeAccessToken, RevokeRefreshToken
from shadow_lib.extensions import api_spec


class RefreshTokenSchema(Schema):
    refresh_token = fields.Str(required=True)


class RefreshTokenResponseSchema(Schema):
    access_token = fields.Str(required=True)


# api_spec.components.schema("LoginSchema", schema=LoginSchema)
api_spec.components.schema("RefreshTokenSchema", schema=RefreshTokenSchema)
api_spec.components.schema(
    "RefreshTokenSuccessSchema", schema=RefreshTokenResponseSchema
)


api_spec.path(
    resource=RefreshToken,
    # api=api,
    app=current_app,
    operations=dict(
        post=dict(
            requestBody={
                "required": True,
                "content": {
                    "application/json": {
                        "schema": "RefreshTokenSchema",
                    }
                },
            },
            summary="Refresh user token.",
            description="Returns new access token if successful.",
            tags=["tokens"],
            responses={
                "200": {
                    "description": "Refresh successful.",
                    "content": {
                        "application/json": {"schema": "RefreshTokenSuccessSchema"}
                    },
                },
                "400": {
                    "description": "Error. Bad request.",
                    "content": {"application/json": {"schema": "GeneralMessageSchema"}},
                },
                "401": {
                    "description": "Error. Tempering with credentials, token expired or wrong token.",
                    "content": {"application/json": {"schema": "GeneralMessageSchema"}},
                },
                "404": {
                    "description": "Error. Token does not exist. User is not active. User doesn't exist anymore.",
                    "content": {"application/json": {"schema": "GeneralMessageSchema"}},
                },
            },
        )
    ),
)


api_spec.path(
    resource=RevokeAccessToken,
    # api=api,
    app=current_app,
    operations=dict(
        post=dict(
            requestBody={
                "required": True,
                "content": {
                    "application/json": {
                        "schema": "RefreshTokenResponseSchema",
                    }
                },
            },
            summary="Revoke user token.",
            description="Revokes access token if successful.",
            tags=["tokens"],
            responses={
                "200": {
                    "description": "Refresh successful.",
                    "content": {"application/json": {"schema": "GeneralMessageSchema"}},
                },
                "401": {
                    "description": "Error. Tempering with credentials, token expired or wrong token.",
                    "content": {"application/json": {"schema": "GeneralMessageSchema"}},
                },
                "404": {
                    "description": "Error. Token does not exist. User is not active. User doesn't exist anymore.",
                    "content": {"application/json": {"schema": "GeneralMessageSchema"}},
                },
            },
        )
    ),
)


api_spec.path(
    resource=RevokeRefreshToken,
    # api=api,
    app=current_app,
    operations=dict(
        post=dict(
            requestBody={
                "required": True,
                "content": {
                    "application/json": {
                        "schema": "RefreshTokenSchema",
                    }
                },
            },
            summary="Revoke user refresh token.",
            description="Revokes refresh token if successful.",
            tags=["tokens"],
            responses={
                "200": {
                    "description": "Refresh successful.",
                    "content": {"application/json": {"schema": "GeneralMessageSchema"}},
                },
                "403": {
                    "description": "Token is the wrong type. Token has expired. Invalid token.",
                    "content": {"application/json": {"schema": "GeneralMessageSchema"}},
                },
                "404": {
                    "description": "Error. Token does not exist. User is not active. User doesn't exist anymore.",
                    "content": {"application/json": {"schema": "GeneralMessageSchema"}},
                },
            },
        )
    ),
)
