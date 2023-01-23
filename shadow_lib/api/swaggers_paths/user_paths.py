from flask import current_app
from marshmallow import Schema, fields, validate
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

from shadow_lib.models.user import UserRoles
from shadow_lib.api.resources import (
    UserChangePasswordResource,
    UserDetailResource,
    UserGetMeResource,
    UserListResource,
    UserRequestPasswordReset,
)

from shadow_lib.api.schemas import (
    ChangePasswordSchema,
    RequestResetPasswordSchema,
    ResetPasswordSchema,
    UserGetMeSchema,
)
from shadow_lib.extensions import api_spec
from shadow_lib.models import User, db


class UserSchema(SQLAlchemyAutoSchema):
    id = fields.UUID(dump_only=True)
    email = fields.Str(required=True, validate=validate.Email())
    password = fields.Str(
        required=True, validate=validate.Length(min=1), load_only=True
    )
    role = fields.Enum(UserRoles, required=True)

    class Meta:
        model = User
        sqla_session = db.session
        load_instance = True


class UserSchemaResponse(Schema):
    message = fields.Str()
    user = fields.Nested(UserSchema)


class UserSchemaMany(Schema):
    users = fields.Nested(UserSchemaResponse(many=True))


api_spec.components.schema("ChangePasswordSchema", schema=ChangePasswordSchema)
api_spec.components.schema(
    "RequestResetPasswordSchema", schema=RequestResetPasswordSchema
)
api_spec.components.schema("ResetPasswordSchema", schema=ResetPasswordSchema)
api_spec.components.schema("UserGetMeSchema", schema=UserGetMeSchema)
api_spec.components.schema("UserSchema", schema=UserSchema)
api_spec.components.schema("UserSchemaResponse", schema=UserSchemaResponse)
api_spec.components.schema(
    "UserSchemaResponseNoMessage", schema=UserSchemaResponse(exclude=["message"])
)
api_spec.components.schema("UserSchemaMany", schema=UserSchemaMany)


# UserDetailResource
api_spec.path(
    resource=UserDetailResource,
    # api=api,
    app=current_app,
    parameters=[
        {
            "name": "id",
            "in": "path",
            "required": True,
            "description": "User id on which perfom actions.",
            "schema": {"type": "string", "format": "uuid"},
        }
    ],
    operations=dict(
        get=dict(
            summary="Returns a user by ID. If it exists.",
            description="Returns a user by ID. If it exists.",
            tags=["users_detail"],
            security=[{"bearerAuth": []}],
            responses={
                "200": {
                    "description": "OK",
                    "content": {
                        "application/json": {"schema": "UserSchemaResponseNoMessage"}
                    },
                },
                "404": {
                    "description": "User not found.",
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
                        "schema": "UserSchema",
                    }
                },
            },
            summary="Updates a user (superadmin only)",
            description="Updates a user",
            tags=["users_detail"],
            responses={
                "200": {
                    "description": "User updated",
                    "content": {"application/json": {"schema": "UserSchemaResponse"}},
                },
                "422": {
                    "description": "List of errors occured in update.",
                    "content": {"application/json": {"schema": "GeneralErrorSchema"}},
                },
            },
        ),
        delete=dict(
            security=[{"bearerAuth": []}],
            summary="Deletes a user (superadmin only)",
            description="Deletes a user",
            tags=["users_detail"],
            responses={
                "200": {
                    "description": "User deleted",
                    "content": {"application/json": {"schema": "GeneralMessageSchema"}},
                },
                "404": {
                    "description": "User not found.",
                    "content": {"application/json": {"schema": "GeneralMessageSchema"}},
                },
            },
        ),
    ),
)


# UserListResource
api_spec.path(
    resource=UserListResource,
    # api=api,
    app=current_app,
    operations=dict(
        get=dict(
            security=[{"bearerAuth": []}],
            summary="Returns a list of users",
            description="Returns a list of users",
            tags=["users"],
            parameters=[
                {
                    "name": "organization_id",
                    "in": "query",
                    "description": "Organization id to filter by (for superadmins only)",
                    "schema": {"type": "array", "items": {"type": "integer"}},
                    "style": "form",
                    "explode": True,
                }
            ],
            responses={
                "200": {
                    "description": "A JSON array of user objects",
                    "content": {"application/json": {"schema": "UserSchemaMany"}},
                },
                "422": {
                    "description": "List of errors occured if filters are not valid.",
                    "content": {"application/json": {"schema": "GeneralErrorSchema"}},
                },
            },
        ),
        post=dict(
            security=[{"bearerAuth": []}],
            requestBody={
                "required": True,
                "content": {
                    "application/json": {
                        "schema": "UserSchema",
                    }
                },
            },
            summary="Creates a user (superadmin only)",
            description="Creates a user",
            tags=["users"],
            responses={
                "201": {
                    "description": "Created",
                    "content": {"application/json": {"schema": "UserSchemaResponse"}},
                },
                "422": {
                    "description": "List of errors occured in creation.",
                    "content": {"application/json": {"schema": "GeneralErrorSchema"}},
                },
            },
        ),
    ),
)

api_spec.path(
    resource=UserGetMeResource,
    # api=api,
    app=current_app,
    operations=dict(
        get=dict(
            security=[{"bearerAuth": []}],
            description="Get me.",
            summary="Get me.",
            tags=["users_detail"],
            responses={
                "200": {
                    "description": "Get me as JSON object",
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "me": {
                                        "$ref": "#/components/schemas/UserGetMeSchema"
                                    }
                                },
                            }
                        }
                    },
                },
            },
        ),
    ),
)


# UserChangePassword
api_spec.path(
    resource=UserChangePasswordResource,
    # api=api,
    app=current_app,
    operations=dict(
        post=dict(
            security=[{"bearerAuth": []}],
            summary="Updates a user password",
            description="Updates a user password",
            tags=["password_actions"],
            requestBody={
                "required": True,
                "content": {
                    "application/json": {
                        "schema": "ChangePasswordSchema",
                    }
                },
            },
            responses={
                "201": {
                    "description": "Updated",
                    "content": {"application/json": {"schema": "GeneralMessageSchema"}},
                },
                "422": {
                    "description": "List of errors occured in update.",
                    "content": {"application/json": {"schema": "GeneralErrorSchema"}},
                },
            },
        ),
    ),
)

# UserResetPassword
api_spec.path(
    path="/api/v1/reset-password",
    # api=api,
    app=current_app,
    operations=dict(
        post=dict(
            summary='Sends an email with a link which contains a "reset-password" temporary token.',
            description='Sends an email with a link which contains a "reset-password" temporary token.',
            tags=["password_actions"],
            requestBody={
                "required": True,
                "content": {
                    "application/json": {
                        "schema": "RequestResetPasswordSchema",
                    }
                },
            },
            responses={
                "201": {
                    "description": "The email was successfully sent",
                    "content": {"application/json": {"schema": "GeneralMessageSchema"}},
                },
                "422": {
                    "description": "List of errors occured in reset process.",
                    "content": {"application/json": {"schema": "GeneralErrorSchema"}},
                },
            },
        ),
    ),
)


# UserResetPassword
api_spec.path(
    resource=UserRequestPasswordReset,
    # api=api,
    app=current_app,
    operations=dict(
        patch=dict(
            summary="Resets a user password",
            description="Resets a user password.",
            tags=["password_actions"],
            requestBody={
                "required": True,
                "content": {
                    "application/json": {
                        "schema": "ResetPasswordSchema",
                    }
                },
            },
            responses={
                "201": {
                    "description": "Reset succeeded",
                    "content": {"application/json": {"schema": "GeneralMessageSchema"}},
                },
                "422": {
                    "description": "List of errors occured in reset process.",
                    "content": {"application/json": {"schema": "GeneralErrorSchema"}},
                },
            },
        ),
        get=dict(
            summary='Validates the "reset-password" temporary token.',
            description='Validates the "reset-password" temporary token',
            tags=["password_actions"],
            responses={
                "201": {
                    "description": "The token is valid",
                    "content": {"application/json": {"schema": "GeneralMessageSchema"}},
                },
                "422": {
                    "description": "List of errors occured in reset process.",
                    "content": {"application/json": {"schema": "GeneralErrorSchema"}},
                },
            },
        ),
    ),
    parameters=[
        {
            "name": "token",
            "in": "path",
            "required": True,
            "description": "Temporary token received by email.",
            "schema": {"type": "string", "format": "uuid"},
        }
    ],
)


# # spec.path(path="/api/v1/enterprises/{id}", resource=EnterpriseDetailResource, api=api, app=current_app)

# api_spec.path(
#     # path="/api/v1/enterprises/{id}",
#     resource=UserGetMeResource,
#     api=api,
#     app=current_app,
#     operations=dict(
#         delete=dict(
#             requestBody={
#                 "required": True,
#                 "content": {
#                     "application/json": {
#                         "schema": "EnterpriseSchema"
#                     }
#                 }
#             },
#             tags=["maledetti"],
#             parameters=[
#                 {
#                     "name": "paperino",
#                     "in": "query",
#                     "required": True,
#                     "description": "scenario id to update.",
#                     "schema": {
#                         "type": "integer"
#                     }
#                 }
#             ],
#             responses={"200": {"description": "enterprise", "content": {"application/json": {"schema": "EnterpriseSchema"}}}}
#         )
#     ),
#     parameters=[
#         {
#             "name": "id",
#             "in": "path",
#             "required": True,
#             "description": "scenario id to update.",
#             "schema": {
#                 "type": "integer"
#             }
#         }
#     ],
# )
