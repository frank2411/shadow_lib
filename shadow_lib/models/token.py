import enum
import uuid
from datetime import timedelta
from typing import Optional

from flask import abort, current_app, g
from sqlalchemy import Boolean, Column, Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func, select
from sqlalchemy.sql.expression import false
from sqlalchemy.types import TIMESTAMP

from shadow_lib.jwt import JwtTokenManager
from shadow_lib.custom_types import TokenDictType

from .db import db
from .model_errors import TOKEN_NOT_EXIST_ERR_MESSAGE, USER_NOT_FOUND_ERR_MESSAGE
from .user import User


class TokensEnum(enum.Enum):
    access = "access"
    refresh = "refresh"


class Token(db.Model):  # type: ignore
    __tablename__ = "tokens"

    id = Column(
        UUID(as_uuid=True), default=uuid.uuid4, nullable=False, primary_key=True
    )

    jti = Column(String(255), unique=True, nullable=False)

    token_type = Column(Enum(TokensEnum), default="access")
    revoked = Column(Boolean, default=False)

    user_id = Column(
        UUID(as_uuid=True), ForeignKey("backoffice_users.id", ondelete="CASCADE")
    )

    created_at = Column(TIMESTAMP, default=func.current_timestamp())
    expires_at = Column(TIMESTAMP)

    @staticmethod
    def set_current_user(token: str) -> "User":
        decoded_token = JwtTokenManager.decode_token(token, "access")

        user_query = select(User).where(
            User.id == decoded_token["user_id"], User.is_active.is_(True)
        )
        user: User = db.session.execute(user_query).unique().scalar_one_or_none()

        if not user:
            abort(404, USER_NOT_FOUND_ERR_MESSAGE)

        g.current_user = user
        return g.current_user

    @staticmethod
    def create_tokens(
        user: "User",
        access_delta: Optional[timedelta] = None,
        refresh_delta: Optional[timedelta] = None,
    ) -> tuple[str, str]:
        user_token_data = {
            "user_id": str(user.id),
            "email": user.email,
            "role": user.role,
        }

        if not access_delta:
            # Minutes expiration
            access_delta = timedelta(minutes=current_app.config["ACCESS_TOKEN_DELTA"])

        if not refresh_delta:
            # Days expiration
            refresh_delta = timedelta(days=current_app.config["REFRESH_TOKEN_DELTA"])

        access_token, access_data = JwtTokenManager.encode_token(
            user_token_data, "access", access_delta
        )

        refresh_token, refresh_data = JwtTokenManager.encode_token(
            user_token_data, "refresh", refresh_delta
        )

        # Lets persist some infos in the database for tracing and revoking
        Token.create_db_tokens(access_data, refresh_data)

        return access_token, refresh_token

    @staticmethod
    def create_db_tokens(
        access_token: TokenDictType, refresh_token: TokenDictType
    ) -> None:
        Token(
            jti=access_token["jti"],
            user_id=access_token["user_id"],
            expires_at=access_token["exp"],
        ).save()

        Token(
            jti=refresh_token["jti"],
            user_id=refresh_token["user_id"],
            token_type="refresh",
            expires_at=refresh_token["exp"],
        ).save()

    @staticmethod
    def refresh_token(refresh_token: str) -> str:
        token = JwtTokenManager.decode_token(refresh_token, "refresh")

        refresh_token_query = select(Token).where(
            Token.jti == token["jti"],
            Token.token_type == "refresh",
            Token.revoked == false(),
        )

        refresh_token = db.session.execute(refresh_token_query).scalar_one_or_none()

        if not refresh_token:
            abort(404, TOKEN_NOT_EXIST_ERR_MESSAGE)

        token_user: User = User.get(token["user_id"])

        # @TODO add check if user is present

        if not token_user.is_active:
            abort(404, USER_NOT_FOUND_ERR_MESSAGE)

        # @TODO we will have to have groups too
        user_token_data = {
            "user_id": str(token_user.id),
            "email": token_user.email,
            "role": token_user.role,
        }

        access_delta = current_app.config["ACCESS_TOKEN_DELTA"]

        # Minutes expiration
        access_token_expiration_delta = timedelta(minutes=access_delta)

        access_token, access_data = JwtTokenManager.encode_token(
            user_token_data, "access", access_token_expiration_delta
        )

        Token(
            jti=access_data["jti"],
            user_id=access_data["user_id"],
            expires_at=access_data["exp"],
        ).save()

        return access_token

    @staticmethod
    def revoke_token(revoke_token: str, token_type: str) -> None:
        token = JwtTokenManager.decode_token(revoke_token, token_type)

        token_query = select(Token).where(
            Token.jti == token["jti"],
            Token.token_type == token_type,
            Token.revoked == false(),
        )

        to_revoke_token = db.session.execute(token_query).scalar_one_or_none()

        if not to_revoke_token:
            abort(404, TOKEN_NOT_EXIST_ERR_MESSAGE)

        to_revoke_token.revoked = True
        to_revoke_token.save()
