from datetime import timedelta

import jwt
import pytest
from flask.testing import FlaskClient
from sqlalchemy.sql import select
from werkzeug.exceptions import HTTPException

from shadow_lib.models import Token, User
from shadow_lib.models.db import DBConfig


class TestCreateToken:
    def test_token_creation(self, db: DBConfig, regular_user: User) -> None:
        access_token, refresh_token = Token.create_tokens(regular_user)
        assert access_token
        assert refresh_token

    def test_token_creation_with_access_delta(self, db: DBConfig, regular_user: User) -> None:
        access_token, refresh_token = Token.create_tokens(regular_user, access_delta=timedelta(minutes=5))
        assert access_token
        assert refresh_token

    def test_token_creation_with_refresh_delta(self, db: DBConfig, regular_user: User) -> None:
        access_token, refresh_token = Token.create_tokens(regular_user, refresh_delta=timedelta(days=1))
        assert access_token
        assert refresh_token

    def test_token_existence(self, db: DBConfig, regular_user: User) -> None:
        access_token, refresh_token = Token.create_tokens(regular_user)
        assert Token.count() == 2


class TestRefreshToken:
    def test_token_refresh_no_json(self, client: FlaskClient) -> None:
        res = client.post("/api/v1/refresh-token")
        res_json = res.get_json()

        assert res.status_code == 400
        assert res_json
        assert res_json["message"] == "Missing JSON in request"

    def test_token_refresh_no_token(self, client: FlaskClient) -> None:
        res = client.post("/api/v1/refresh-token", json={"empty": ""})
        res_json = res.get_json()

        assert res.status_code == 403
        assert res_json
        assert res_json["message"] == "No token provided"

    def test_token_refresh_malformed_token(self, client: FlaskClient, db: DBConfig) -> None:
        res = client.post("/api/v1/refresh-token", json={"refresh_token": "123123123"})
        res_json = res.get_json()

        assert res.status_code == 401
        assert res_json
        assert res_json["message"] == "Token claims are missing or token is malformed"

    def test_token_refresh_unexistent_token(self, client: FlaskClient, db: DBConfig, fake_refresh_token: str) -> None:
        res = client.post("/api/v1/refresh-token", json={"refresh_token": fake_refresh_token})
        res_json = res.get_json()

        assert res.status_code == 404
        assert res_json
        assert res_json["message"] == "Token does not exist"

    def test_token_refresh_no_existent_user(self, client: FlaskClient, db: DBConfig, deactivated_refresh_token: str) -> None:
        res = client.post("/api/v1/refresh-token", json={"refresh_token": deactivated_refresh_token})
        res_json = res.get_json()

        assert res.status_code == 404
        assert res_json
        assert res_json["message"] == "User not found"

    def test_token_refresh_expired(self, client: FlaskClient, db: DBConfig, expired_refresh_token: str) -> None:
        res = client.post("/api/v1/refresh-token", json={"refresh_token": expired_refresh_token})
        res_json = res.get_json()

        assert res.status_code == 401
        assert res_json
        assert res_json["message"] == "Token has expired. Please login again"

    def test_token_refresh_success(self, client: FlaskClient, db: DBConfig, refresh_token: str) -> None:
        res = client.post("/api/v1/refresh-token", json={"refresh_token": refresh_token})
        res_json = res.get_json()

        assert res.status_code == 200
        assert res_json
        assert "access_token" in res_json


class TestRevokeToken:
    def test_revoke_access_token_no_json(self, client: FlaskClient) -> None:
        res = client.post("/api/v1/revoke-access-token")
        res_json = res.get_json()

        assert res.status_code == 400
        assert res_json
        assert res_json["message"] == "Missing JSON in request"

    def test_revoke_access_token_token_malformed(self, client: FlaskClient, db: DBConfig) -> None:
        res = client.post("/api/v1/revoke-access-token", json={"access_token": "123123123"})
        res_json = res.get_json()

        assert res.status_code == 401
        assert res_json
        assert res_json["message"] == "Token claims are missing or token is malformed"

    def test_revoke_access_token_already_revoked(self, client: FlaskClient, db: DBConfig, revoked_access_token: str) -> None:
        res = client.post("/api/v1/revoke-access-token", json={"access_token": revoked_access_token})
        res_json = res.get_json()

        assert res.status_code == 404
        assert res_json
        assert res_json["message"] == "Token does not exist"

    def test_revoke_access_token_success(self, client: FlaskClient, db: DBConfig, access_token: str) -> None:
        res = client.post("/api/v1/revoke-access-token", json={"access_token": access_token})
        res_json = res.get_json()

        payload = jwt.decode(access_token, options={"verify_signature": False, "verify_exp": False})

        assert res.status_code == 200
        assert res_json
        assert res_json["message"] == "Token has been revoked"
        assert db.session.execute(select(Token).where(Token.jti == payload["jti"])).scalar_one_or_none().revoked is True

    def test_revoke_refresh_token_no_json(self, client: FlaskClient) -> None:
        res = client.post("/api/v1/revoke-refresh-token")
        res_json = res.get_json()

        assert res.status_code == 400
        assert res_json
        assert res_json["message"] == "Missing JSON in request"

    def test_revoke_refesh_token_malformed(self, client: FlaskClient, db: DBConfig) -> None:
        res = client.post("/api/v1/revoke-refresh-token", json={"refresh_token": "123123123"})
        res_json = res.get_json()

        assert res.status_code == 401
        assert res_json
        assert res_json["message"] == "Token claims are missing or token is malformed"

    def test_revoke_refesh_token_not_found(self, client: FlaskClient, db: DBConfig, fake_refresh_token: str) -> None:
        res = client.post("/api/v1/revoke-refresh-token", json={"refresh_token": fake_refresh_token})
        res_json = res.get_json()

        assert res.status_code == 404
        assert res_json
        assert res_json["message"] == "Token does not exist"

    def test_revoke_refresh_token_already_revoked(self, client: FlaskClient, db: DBConfig, revoked_refresh_token: str) -> None:
        res = client.post(
            "/api/v1/revoke-refresh-token",
            json={"refresh_token": revoked_refresh_token},
        )
        res_json = res.get_json()

        assert res.status_code == 404
        assert res_json
        assert res_json["message"] == "Token does not exist"

    def test_revoke_refresh_token_success(self, client: FlaskClient, db: DBConfig, refresh_token: str) -> None:
        res = client.post("/api/v1/revoke-refresh-token", json={"refresh_token": refresh_token})
        res_json = res.get_json()

        payload = jwt.decode(refresh_token, options={"verify_signature": False, "verify_exp": False})

        assert res.status_code == 200
        assert res_json
        assert res_json["message"] == "Token has been revoked"
        assert db.session.execute(select(Token).where(Token.jti == payload["jti"])).scalar_one_or_none().revoked is True

    def test_revoke_access_token_not_provided(self, client: FlaskClient, db: DBConfig) -> None:
        res = client.post("/api/v1/revoke-access-token", json={"empty": ""})
        res_json = res.get_json()

        assert res.status_code == 403
        assert res_json
        assert res_json["message"] == "No token provided"

    def test_revoke_refresh_token_not_provided(self, client: FlaskClient, db: DBConfig) -> None:
        res = client.post("/api/v1/revoke-refresh-token", json={"empty": ""})
        res_json = res.get_json()

        assert res.status_code == 403
        assert res_json
        assert res_json["message"] == "No token provided"


class TestSetCurrentUser:
    def test_set_current_user_malformed_token(self, db: DBConfig, access_token: str) -> None:
        token = "123123"

        with pytest.raises(HTTPException) as httperror:
            Token.set_current_user(token)

        assert httperror.value.code == 401
        assert httperror.value.description == "Token claims are missing or token is malformed"

    def test_set_current_user_expired_token(self, db: DBConfig, expired_access_token: str) -> None:
        token = expired_access_token

        with pytest.raises(HTTPException) as httperror:
            Token.set_current_user(token)

        assert httperror.value.code == 401

        assert httperror.value.description == "Token has expired. Please login again"

    def test_set_current_user_user_not_found(self, db: DBConfig, access_token: str) -> None:
        payload = jwt.decode(access_token, options={"verify_signature": False, "verify_exp": False})

        user = User.get(payload["user_id"])
        user.is_active = False
        user.save()

        token = access_token

        with pytest.raises(HTTPException) as httperror:
            Token.set_current_user(token)

        assert httperror.value.code == 404
        assert httperror.value.description == "User not found"

    def test_set_current_user_valid_token(self, db: DBConfig, access_token: str) -> None:
        payload = jwt.decode(access_token, options={"verify_signature": False, "verify_exp": False})

        token = access_token
        user = Token.set_current_user(token)
        assert user is not None
        assert str(user.id) == payload["user_id"]

    def test_set_current_user_wrong_token(self, db: DBConfig, refresh_token: str) -> None:
        token = refresh_token
        with pytest.raises(HTTPException) as httperror:
            Token.set_current_user(token)

        assert httperror.value.code == 401
        assert httperror.value.description == "Wrong token type"
