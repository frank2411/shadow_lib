from typing import Any, Mapping, Optional

from flask import current_app, g
from marshmallow import (
    Schema,
    ValidationError,
    fields,
    post_dump,
    post_load,
    validate,
    validates,
    validates_schema,
)
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

# from marshmallow_sqlalchemy.fields import RelatedList
from sqlalchemy.sql import select

from shadow_lib.models.user import UserRoles
from shadow_lib.models import User, db
from shadow_lib.notify import Notify

# from .custom_fields import FixedRelated


class UserSchema(SQLAlchemyAutoSchema):

    error_messages = {
        "password_not_provided": "Password must not be empty",
        "role_does_not_exist": "Role does not exist",
        "role_not_permitted": "To add this role you must have higher permissions.",
        "organization_not_found": "Organization hasn't been found in the database",
        "value_is_empty": "Field cannot be empty",
        "email_exists": "Email already exists",
    }

    valid_roles = [role.value for role in UserRoles]

    def __init__(self, is_creation: bool = False, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.is_creation = is_creation

        self.current_user_role = g.current_user.role
        self.is_superadmin = (
            True if self.current_user_role == UserRoles.superadmin else False
        )

        if self.instance:
            self.original_password = self.instance.password

    id = fields.UUID(dump_only=True)
    email = fields.Str(required=True, validate=validate.Email())
    password = fields.Str(required=True, validate=validate.Length(min=1))
    role = fields.Method("get_role_value", deserialize="validate_role")

    def validate_role(self, value: str) -> Optional[str]:
        if value not in self.valid_roles:
            raise ValidationError(self.error_messages["role_does_not_exist"])

        # @TODO: Decomment when we have the admin role
        # Commenting out this part because a regular user cannot create or update a user anyway
        # --> not applicable
        # if (
        #     value == UserRoles.superadmin
        #     and self.current_user_role != UserRoles.superadmin
        # ):
        #     raise ValidationError(self.error_messages["role_not_permitted"])

        return value

    def get_role_value(self, obj: Any) -> str:
        role: str = obj.role.value
        return role

    @validates("email")
    def validate_email_not_existing(self, value: str) -> None:
        user_query = select(User).where(User.email == value)
        user: "User" = db.session.execute(user_query).unique().scalar_one_or_none()
        if user:
            raise ValidationError(self.error_messages["email_exists"])

    # @pre_load
    # def check_required_fields(self, data: dict[str, str], **kwargs: Any) -> dict[str, str]:
    #     role = data.get("role", None)

    #     # If i'm creating a superadmin the organization is not necessary
    #     # if self.is_superadmin and role == UserRoles.superadmin:
    #     #     del self.load_fields["organization"]
    #     #     del self.load_fields["groups"]

    #     # @TODO: Decomment when we have the admin role
    #     # If not a superadmin and I'm updating I have to exlude the organization and group fields
    #     # Commenting out this part because a regular user cannot create or update a user anyway
    #     # --> not applicable
    #     # if not self.is_superadmin and self.partial:
    #     #     if data.get("organization"):
    #     #         del data["organization"]

    #     #     if data.get("groups"):
    #     #         del data["groups"]

    #     return data

    @post_load
    def set_new_password(self, instance: "UserSchema", **kwargs: Any) -> "UserSchema":
        if self.partial and instance.password != self.original_password:
            # ignore type checking below because of incompatibility between str and fields.String only in type checking
            instance.password = User.set_password_hash(instance.password)  # type: ignore
        return instance

    @post_dump
    def exclude_password(self, obj: dict[str, str], **kwargs: Any) -> Mapping[str, str]:
        if self.is_creation:
            del obj["password"]
        return obj

    class Meta:
        model = User
        sqla_session = db.session
        load_instance = True


class UserGetMeSchema(SQLAlchemyAutoSchema):

    role = fields.Method("get_role_value")

    def get_role_value(self, obj: Any) -> str:
        role: str = obj.role
        return role

    class Meta:
        model = User
        sqla_session = db.session
        load_instance = True
        exclude = (
            "password",
            "is_active",
            "temporary_token",
            "tokens",
        )


class ChangePasswordSchema(Schema):
    error_messages = {
        "passwords_mismatch": "Passwords are not the same",
        "old_password_mismatch": "Wrong old password",
        "old_password_not_provided": "Old Password must not be empty",
        "password_not_provided": "Password must not be empty",
        "password_too_short_admin": "Password must not be at least 12 characters long",
        "password_too_short_user": "Password must not be at least 8 characters long",
        "password_format_not_valid": "Password isn't satisfying its structure needs",
    }

    old_password = fields.String(
        required=True,
        validate=validate.Length(
            min=1, error=error_messages["old_password_not_provided"]
        ),
    )
    new_password = fields.String(
        required=True,
        validate=validate.Length(min=1, error=error_messages["password_not_provided"]),
    )
    new_password_confirm = fields.String(required=True)

    @validates("old_password")
    def validate_old_password(self, value: str) -> None:
        old_password = value
        password_valid = g.current_user.check_password(old_password)

        if not password_valid:
            raise ValidationError(self.error_messages["old_password_mismatch"])

    @validates_schema
    def validate_new_password_match(
        self, data: Mapping[str, str], **kwargs: Any
    ) -> None:
        if data["new_password"] != data["new_password_confirm"]:
            raise ValidationError(
                self.error_messages["passwords_mismatch"], "passwords"
            )

    @post_load
    def set_new_password(self, data: Mapping[str, str], **kwargs: Any) -> None:
        g.current_user.password = User.set_password_hash(data["new_password"])
        g.current_user.save(password_updated=True)


class ResetPasswordSchema(SQLAlchemyAutoSchema):
    error_messages = {
        "password_not_provided": "Password must not be empty",
        "password_too_short_admin": "Password must not be at least 12 characters long",
        "password_too_short_user": "Password must not be at least 8 characters long",
        "password_format_not_valid": "Password isn't satisfying its structure needs",
    }

    password = fields.String(required=True, validate=validate.Length(min=1))

    @post_load
    def set_new_password(self, data: Mapping[str, str], **kwargs: Any) -> None:
        self.instance.password = User.set_password_hash(data["password"])
        self.instance.save(password_updated=True)

    class Meta:
        model = User
        fields = ("password",)


class RequestResetPasswordSchema(Schema):

    email = fields.Email(required=True)

    class Meta:
        fields = ("email",)

    @post_load
    def create_temporary_token_and_send_email(
        self, data: Mapping[str, str], **kwargs: Any
    ) -> None:
        user = User.get_user_for_reset_password(data.get("email", ""))
        if not user:  # Fake successful password request
            return

        user.create_temporary_token()

        # @TODO send mail logic
        message: Notify = Notify(
            email_template="reset_password",
            subject="Reset Password",
            receiver=user.email,
            data={
                "temporary_token": user.temporary_token,
                "user": user,
                "base_url": current_app.config["FRONTEND_URL"],
            },
        )

        message.send()
