import uuid
import enum

import bcrypt
from flask import abort

# from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, String
from sqlalchemy import Boolean, Column, DateTime, Enum, String
from sqlalchemy.dialects.postgresql import UUID

# from sqlalchemy.orm import joinedload, relationship
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func, select

from .db import db
from .model_errors import BAD_CREDENTIALS_ERR_MESSAGE, USER_NOT_FOUND_ERR_MESSAGE


class UserRoles(str, enum.Enum):
    superadmin = "superadmin"  # pylint: disable=invalid-name
    user = "user"  # pylint: disable=invalid-name


class User(db.Model):  # type: ignore
    """
    User model
    """

    __tablename__ = "backoffice_users"
    __repr_attrs__ = ["email"]

    id = Column(
        UUID(as_uuid=True), default=uuid.uuid4, nullable=False, primary_key=True
    )

    first_name = Column(String(255))
    last_name = Column(String(255))

    email = Column(String(255), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    role = Column(Enum(UserRoles), nullable=False, default="user")

    is_active = Column(Boolean, nullable=False, default=False)

    last_password_update = Column(
        DateTime(timezone=True), default=func.current_timestamp()
    )
    last_login_date = Column(DateTime(timezone=True), default=func.current_timestamp())

    last_password_update = Column(
        DateTime(timezone=True), default=func.current_timestamp()
    )
    last_login_date = Column(DateTime(timezone=True), default=func.current_timestamp())

    # Token user for password reset and first access
    temporary_token = Column(String(255))

    tokens = relationship(
        "Token",
        backref="user",
        lazy="select",
        cascade="all,delete-orphan",
        passive_deletes=True,
    )

    authors = relationship(
        "Author",
        backref="created_by",
        lazy="select",
        cascade="all,delete-orphan",
        passive_deletes=True,
    )

    books = relationship(
        "Book",
        backref="created_by",
        lazy="select",
        cascade="all,delete-orphan",
        passive_deletes=True,
    )

    customers = relationship(
        "Customer",
        backref="created_by",
        lazy="select",
        cascade="all,delete-orphan",
        passive_deletes=True,
    )

    orders = relationship(
        "Order",
        backref="created_by",
        lazy="select",
        cascade="all,delete-orphan",
        passive_deletes=True,
    )

    @staticmethod
    def get_user(user_id: uuid.UUID, current_user: "User") -> "User":
        user_query = select(User).where(User.id == user_id)
        user: "User" = db.session.execute(user_query).unique().scalar_one_or_none()

        if not user:
            return abort(404, USER_NOT_FOUND_ERR_MESSAGE)

        return user

    @staticmethod
    def get_users(current_user: "User") -> list["User"]:
        user_query = select(User)

        users: list[User] = db.session.execute(user_query).unique().scalars().all()

        return users

    @staticmethod
    def set_password_hash(raw_password: str) -> str:
        salt = bcrypt.gensalt(rounds=10)
        hashed = bcrypt.hashpw(raw_password.encode(), salt)
        return hashed.decode()

    @staticmethod
    def get_user_for_login(email: str, raw_password: str) -> "User":
        user_query = select(User).where(User.email == email, User.is_active.is_(True))
        user: "User" = db.session.execute(user_query).unique().scalar_one_or_none()

        if not user:
            return abort(400, BAD_CREDENTIALS_ERR_MESSAGE)

        password_valid = user.check_password(raw_password)

        if not password_valid:
            abort(400, BAD_CREDENTIALS_ERR_MESSAGE)

        user.last_login_date = func.current_timestamp()
        user.save()

        return user

    @staticmethod
    def get_user_for_reset_password(email: str) -> "User":
        user_query = select(User).where(User.email == email, User.is_active.is_(True))

        # https://docs.sqlalchemy.org/en/14/tutorial/
        # WARNING: This unique it's not the SQL index. Check links above.
        user: "User" = db.session.execute(user_query).unique().scalar_one_or_none()
        return user

    # To be implemented after the token module is imported and adapted from the example repository
    @staticmethod
    def validate_temporary_token(token: str) -> "User":
        """
        Either validates the token and return the user or it raises a 404 error
        """
        user_query = select(User).where(User.temporary_token == token)

        # https://docs.sqlalchemy.org/en/14/tutorial/
        # WARNING: This unique it's not the SQL index. Check links above.
        user: "User" = db.session.execute(user_query).unique().scalar_one_or_none()

        if not user:
            abort(404, "Token not valid")

        return user

    def create_temporary_token(self) -> None:
        token = uuid.uuid4()
        self.temporary_token = token
        self.save()

    def check_password(self, raw_password: str) -> bool:
        return bcrypt.checkpw(raw_password.encode(), self.password.encode())

    def save(self, password_updated: bool = False) -> None:
        if not self.id:
            self.password = User.set_password_hash(self.password)

        if password_updated:
            self.last_password_update = func.current_timestamp()

        self.session.add(self)
        self.session.commit()

    def delete(self) -> None:
        self.session.delete(self)
        self.session.commit()
