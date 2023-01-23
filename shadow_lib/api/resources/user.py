import uuid

from flask import current_app, g, request
from flask_restful import Resource
from marshmallow import ValidationError

from shadow_lib.decorators import (
    authenticate_user,
    check_bearer_token,
    redirect_if_not_superadmin,
)

# from edfsf.microservice_utils.rabbitmq.rabbitmq_exceptions import RabbitMQPublisherException
# from shadow_lib.extensions import rabbitmq_ext
from shadow_lib.api.schemas import (
    ChangePasswordSchema,
    RequestResetPasswordSchema,
    ResetPasswordSchema,
    UserGetMeSchema,
    UserSchema,
)
from shadow_lib.custom_types import ErrorResponseType, SuccessResponseType
from shadow_lib.models import User


class UserDetailResource(Resource):

    method_decorators = [
        redirect_if_not_superadmin,
        authenticate_user,
        check_bearer_token,
    ]
    auto_update_fields = [
        "email",
        "password",
        "role",
        "is_active",
    ]

    def get(self, user_id: uuid.UUID) -> SuccessResponseType:
        schema = UserSchema(exclude=["password"])
        user = User.get_user(user_id, g.current_user)
        return {"user": schema.dump(user)}

    def patch(self, user_id: uuid.UUID) -> SuccessResponseType | ErrorResponseType:
        user = User.get_user(user_id, g.current_user)
        schema = UserSchema(partial=True, instance=user)

        # If I'm modifying myself so email and password are excluded
        # this way can track this change separately
        # if user.id == g.current_user.id and user.role != "superadmin":
        #     schema = UserSchema(
        #         partial=True, exclude=self.auto_update_fields, instance=user
        #     )

        try:
            user = schema.load(request.json)
        except ValidationError as err:
            return err.messages, 422

        user.save()
        return {"message": "user updated", "user": schema.dump(user)}

    def delete(self, user_id: uuid.UUID) -> SuccessResponseType:
        user = User.get_user(user_id, g.current_user)
        user.delete()
        current_app.logger.info(f"user {user.id} deleted")
        return {"message": "user deleted"}


class UserListResource(Resource):
    """Creation and get_all"""

    # Uncomment after implementing authentication mechanisms (related to the token module)
    method_decorators = [
        redirect_if_not_superadmin,
        authenticate_user,
        check_bearer_token,
    ]

    def get(self) -> SuccessResponseType:
        schema = UserSchema(many=True, exclude=["password"])
        users = User.get_users(g.current_user)
        return {"users": schema.dump(users)}

    def post(self) -> SuccessResponseType | ErrorResponseType:
        try:
            schema = UserSchema(is_creation=True)
            user: User = schema.load(request.json)
        except ValidationError as err:
            return err.messages, 422

        user.is_active = True
        user.save()

        current_app.logger.info(f"user {user.id} created")

        # rabbit_message = "success"
        # dispatch_message = {"action": "user.created", "payload": schema.dump(user)}

        # try:
        #     rabbitmq_ext.publish_message(dispatch_message)
        #     current_app.logger.info("RabbitMQ dispatch successful")
        # except RabbitMQPublisherException as e:
        #     rabbit_message = "failed"
        #     current_app.logger.error(f"RabbitMQ dispatch failed: {e}")

        # return {
        #     "message": "user created",
        #     "user": schema.dump(user),
        #     "message_status": rabbit_message,
        # }, 201

        return {
            "message": "user created",
            "user": schema.dump(user),
        }, 201


class UserGetMeResource(Resource):

    method_decorators = [authenticate_user, check_bearer_token]

    def get(self) -> SuccessResponseType:
        schema = UserGetMeSchema()
        return {"me": schema.dump(g.current_user)}


class UserChangePasswordResource(Resource):
    method_decorators = [authenticate_user, check_bearer_token]

    def post(self) -> SuccessResponseType | ErrorResponseType:
        schema = ChangePasswordSchema()
        try:
            schema = schema.load(request.json)
        except ValidationError as err:
            return err.messages, 422

        return {"message": "password updated"}, 201


class UserRequestPasswordReset(Resource):
    def get(self, token: str) -> SuccessResponseType:
        User.validate_temporary_token(token)
        return {"message": "token valid"}, 200

    def post(self) -> SuccessResponseType | ErrorResponseType:
        schema = RequestResetPasswordSchema()
        try:
            schema = schema.load(request.json)
        except ValidationError as err:
            return err.messages, 422

        return {"message": "Request sent"}, 200

    def patch(self, token: str) -> SuccessResponseType | ErrorResponseType:
        user = User.validate_temporary_token(token)
        schema = ResetPasswordSchema(instance=user)

        try:
            schema = schema.load(request.json)
        except ValidationError as err:
            return err.messages, 422

        return {"message": "Password reset ok"}, 200
