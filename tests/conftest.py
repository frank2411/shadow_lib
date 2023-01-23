import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Callable, Dict, Generator, cast

import jwt
import pytest
from flask import Flask, g
from flask.testing import FlaskClient

from shadow_lib.jwt import JwtTokenManager
from shadow_lib.app import create_app
from shadow_lib.models import Token, User, Author, Book, Customer, Order, BorrowedBook
from shadow_lib.models import db as rawdb
from shadow_lib.models.db import DBConfig

RESOURCES = Path(__file__).parent / "resources"
REPOSITORY_ROOT_DIR = Path(__file__).parent.parent


@pytest.fixture()
def resources() -> Path:
    return RESOURCES


@pytest.fixture
def app() -> Flask:
    app = create_app(testing=True)
    return app


@pytest.fixture
def client(app: Flask) -> Generator[FlaskClient, None, None]:
    yield app.test_client()


@pytest.fixture
def db(app: Flask) -> Generator[DBConfig, None, None]:
    with app.app_context():
        rawdb.init_db()

        yield rawdb

        rawdb.session.close()
        rawdb.drop_db()


@pytest.fixture
def superadmin(db: DBConfig) -> User:
    user = User(email="superuser@email.com", password="test", is_active=True, role="superadmin")
    user.save()
    return user


@pytest.fixture
def regular_user(db: DBConfig) -> User:
    # A simple user MUST always have an organization
    user = User(
        email="normaluser@email.com",
        password="test",
        is_active=True,
        role="user"
    )
    user.save()
    return user


@pytest.fixture
def regular_user_deactivated(db: DBConfig) -> User:

    user = User(
        email="deactivateduser@email.com",
        password="test",
        is_active=False,
        role="user"
    )

    user.save()

    return user


@pytest.fixture
def reset_password_user(db: DBConfig) -> User:
    user = User(
        email="resetuser@email.com",
        password="test",
        role="user",
        is_active=True,
        temporary_token=uuid.uuid4(),
    )

    user.save()

    return user


@pytest.fixture
def simple_author(db: DBConfig, regular_user: User) -> Author:

    author = Author(
        first_name="test",
        last_name="test",
        release_date="2022-10-10",
        created_by_id=regular_user.id
    )
    author.save()
    return author


@pytest.fixture
def simple_book(db: DBConfig, regular_user: User, simple_author: Author) -> Book:

    book = Book(
        title="test",
        EAN="test",
        SKU="TEST",
        created_by_id=regular_user.id,
        release_date="2022-10-10",
        qty=20,
    )

    book.authors.append(simple_author)

    book.save()
    return book


@pytest.fixture
def simple_book_2(db: DBConfig, regular_user: User, simple_author: Author) -> Book:

    book = Book(
        title="test",
        EAN="test",
        SKU="TEST",
        created_by_id=regular_user.id,
        release_date="2022-10-10",
        qty=20,
    )

    book.authors.append(simple_author)

    book.save()
    return book


@pytest.fixture
def simple_order(db: DBConfig, simple_book: Book, simple_customer: Customer):

    order = Order(
        customer_id=str(simple_customer.id),
        due_date="2022-10-10",
    )

    bb = BorrowedBook(
        book_id=simple_book.id,
        qty=4,
    )

    order.borrowed_books.append(bb)
    order.save()

    return order


@pytest.fixture
def simple_order_2_books(db: DBConfig, simple_book: Book, simple_book_2: Book, simple_customer: Customer):

    order = Order(
        customer_id=str(simple_customer.id),
        due_date="2022-10-10",
    )

    bb = BorrowedBook(
        book_id=simple_book.id,
        qty=4,
    )

    bb2 = BorrowedBook(
        book_id=simple_book_2.id,
        qty=10,
    )

    order.borrowed_books.append(bb)
    order.borrowed_books.append(bb2)
    order.save()

    return order


@pytest.fixture
def simple_customer(db: DBConfig, regular_user: User) -> Book:

    customer = Customer(
        fullname="customer test",
        document_type="generic_id",
        document_id="1231231231223",
        created_by_id=regular_user.id,
    )

    customer.save()
    return customer


# temporary fixture to set current_user
@pytest.fixture
def set_current_user() -> Callable[[User], User]:
    def _fn(a_user: User) -> User:
        g.current_user = a_user
        return a_user

    return _fn


@pytest.fixture
def generic_headers() -> Dict[str, str]:

    headers = {
        "content-type": "application/json",
        "authorization": "Bearer 123123123123",
    }

    return headers


# @pytest.fixture
# def superadmin_headers(client, db, superadmin):
#     data = {"email": superadmin.email, "password": "test"}

#     res = client.post("/api/v1/login", json=data)
#     res_json = res.get_json()
#     access_token = res_json["access_token"]

#     return {
#         "content-type": "application/json",
#         "authorization": f"Bearer {access_token}",
#     }


@pytest.fixture
def access_token(app: Flask, db: DBConfig, regular_user: User) -> str:
    access_delta = app.config["ACCESS_TOKEN_DELTA"]
    access_token_expiration_delta = timedelta(minutes=access_delta)

    user_token_data = {
        "user_id": str(regular_user.id),
        "email": regular_user.email,
        "role": regular_user.role.value,
    }

    access_token, access_data = JwtTokenManager.encode_token(user_token_data, "access", access_token_expiration_delta)

    Token(
        jti=access_data["jti"],
        user_id=access_data["user_id"],
        expires_at=access_data["exp"],
    ).save()

    return access_token


@pytest.fixture
def expired_access_token(app: Flask, db: DBConfig, regular_user: User) -> str:
    secret = app.config["SECRET_KEY"]

    very_old_datetime = datetime.utcnow() - timedelta(days=20)

    token_data = {
        "user_id": str(regular_user.id),
        "email": regular_user.email,
        "role": regular_user.role.value,
        "iat": very_old_datetime,
        "nbf": very_old_datetime,
        "jti": str(uuid.uuid4()),
        "iss": "user_service",
        "type": "access_token",
        "exp": very_old_datetime,
    }

    encoded_token: str = jwt.encode(token_data, secret, algorithm="HS256")
    return encoded_token


@pytest.fixture
def refresh_token(app: Flask, db: DBConfig, regular_user: User) -> str:

    refresh_delta = app.config["REFRESH_TOKEN_DELTA"]
    refresh_token_expiration_delta = timedelta(minutes=refresh_delta)

    user_token_data = {
        "user_id": str(regular_user.id),
        "email": regular_user.email,
        "role": regular_user.role.value,
    }

    refresh_token, refresh_data = JwtTokenManager.encode_token(user_token_data, "refresh", refresh_token_expiration_delta)

    Token(
        jti=refresh_data["jti"],
        user_id=refresh_data["user_id"],
        expires_at=refresh_data["exp"],
        token_type="refresh",
    ).save()

    return refresh_token


@pytest.fixture
def expired_refresh_token(app: Flask, db: DBConfig, regular_user: User) -> str:
    secret = app.config["SECRET_KEY"]

    very_old_datetime = datetime.utcnow() - timedelta(days=20)

    token_data = {
        "user_id": str(regular_user.id),
        "email": regular_user.email,
        "role": regular_user.role.value,
        "iat": very_old_datetime,
        "nbf": very_old_datetime,
        "jti": str(uuid.uuid4()),
        "iss": "user_service",
        "type": "refresh",
        "exp": very_old_datetime,
    }

    encoded_token: str = jwt.encode(token_data, secret, algorithm="HS256")

    return encoded_token


@pytest.fixture
def fake_refresh_token(app: Flask, db: DBConfig, regular_user: User) -> str:

    secret = app.config["SECRET_KEY"]

    exp = datetime.utcnow() + timedelta(days=20)

    token_data = {
        "user_id": str(regular_user.id),
        "email": regular_user.email,
        "role": regular_user.role.value,
        "iat": datetime.utcnow(),
        "nbf": datetime.utcnow(),
        "jti": str(uuid.uuid4()),
        "iss": "user_service",
        "type": "refresh",
        "exp": exp,
    }

    encoded_token: str = jwt.encode(token_data, secret, algorithm="HS256")

    return encoded_token


@pytest.fixture
def revoked_access_token(app: Flask, db: DBConfig, regular_user: User) -> str:

    secret = app.config["SECRET_KEY"]

    exp = datetime.utcnow() + timedelta(days=20)

    token_data = {
        "user_id": str(regular_user.id),
        "email": regular_user.email,
        "role": regular_user.role.value,
        "iat": datetime.utcnow(),
        "nbf": datetime.utcnow(),
        "jti": str(uuid.uuid4()),
        "iss": "user_service",
        "type": "access",
        "exp": exp,
    }

    encoded_token: str = jwt.encode(token_data, secret, algorithm="HS256")

    revoked_access_token = Token(
        jti=token_data["jti"],
        user_id=regular_user.id,
        token_type="access",
        expires_at=token_data["exp"],
        revoked=True,
    )

    revoked_access_token.save()
    return encoded_token


@pytest.fixture
def revoked_refresh_token(app: Flask, db: DBConfig, regular_user: User) -> str:
    secret = app.config["SECRET_KEY"]

    exp = datetime.utcnow() + timedelta(days=20)

    token_data = {
        "user_id": str(regular_user.id),
        "email": regular_user.email,
        "role": regular_user.role.value,
        "iat": datetime.utcnow(),
        "nbf": datetime.utcnow(),
        "jti": str(uuid.uuid4()),
        "iss": "user_service",
        "type": "refresh",
        "exp": exp,
    }

    encoded_token: str = jwt.encode(token_data, secret, algorithm="HS256")

    revoked_access_token = Token(
        jti=token_data["jti"],
        user_id=regular_user.id,
        token_type="access",
        expires_at=token_data["exp"],
        revoked=True,
    )

    revoked_access_token.save()
    return encoded_token


@pytest.fixture
def deactivated_refresh_token(app: Flask, db: DBConfig, regular_user_deactivated: User) -> str:

    refresh_delta = app.config["REFRESH_TOKEN_DELTA"]
    refresh_token_expiration_delta = timedelta(minutes=refresh_delta)

    user_token_data = {
        "user_id": str(regular_user_deactivated.id),
        "email": regular_user_deactivated.email,
        "role": regular_user_deactivated.role.value,
    }

    refresh_token, refresh_data = JwtTokenManager.encode_token(user_token_data, "refresh", refresh_token_expiration_delta)

    refresh_token_db = Token(
        jti=refresh_data["jti"],
        user_id=regular_user_deactivated.id,
        token_type="refresh",
        expires_at=str(refresh_data["exp"]),
    )

    refresh_token_db.save()
    return refresh_token


@pytest.fixture
def regular_user_headers(client: FlaskClient, db: DBConfig, regular_user: User) -> dict[str, str]:
    data = {"email": regular_user.email, "password": "test"}

    res = client.post("/api/v1/login", json=data)
    res_json = cast(dict[str, str], res.get_json())
    access_token = res_json["access_token"]

    return {
        "content-type": "application/json",
        "authorization": f"Bearer {access_token}",
    }


@pytest.fixture
def superadmin_headers(client: FlaskClient, db: DBConfig, superadmin: User) -> dict[str, str]:
    data = {"email": superadmin.email, "password": "test"}

    res = client.post("/api/v1/login", json=data)
    res_json = cast(dict[str, str], res.get_json())
    access_token = res_json["access_token"]

    return {
        "content-type": "application/json",
        "authorization": f"Bearer {access_token}",
    }


@pytest.fixture
def random_uuid() -> Generator:
    yield uuid.uuid4()
