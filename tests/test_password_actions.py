from typing import Mapping

from flask import Flask
from flask.testing import FlaskClient

from shadow_lib.models import User
from shadow_lib.models.db import DBConfig


class TestResetPassword:
    def test_request_reset_password_no_email(self, db: DBConfig, client: FlaskClient) -> None:
        data = {"email": ""}
        res = client.post("/api/v1/users/reset-password", json=data)
        assert res.status_code == 422

    def test_request_reset_password_no_user(self, db: DBConfig, client: FlaskClient) -> None:
        json = {"email": "fake@user.it"}
        res = client.post("/api/v1/users/reset-password", json=json)
        assert res.status_code == 200

    def test_request_reset_password_method_not_allowed_post(self, db: DBConfig, client: FlaskClient) -> None:
        res = client.post("/api/v1/users/reset-password/12123123120")
        assert res.status_code == 405

    def test_request_reset_password_patch_method_not_authorized(self, db: DBConfig, client: FlaskClient) -> None:
        res = client.patch("/api/v1/users/reset-password/")
        assert res.status_code == 405

    def test_request_reset_password_patch_method_not_found(self, db: DBConfig, client: FlaskClient) -> None:
        res = client.patch("/api/v1/users/reset-password/123123")
        assert res.status_code == 404

    def test_request_reset_password_regular_user_200(
        self,
        app: Flask,
        db: DBConfig,
        client: FlaskClient,
        regular_user: User,
    ) -> None:
        check_id = regular_user.id
        check_email = regular_user.email
        json = {"email": regular_user.email}
        res = client.post("/api/v1/users/reset-password", json=json)

        check_user = User.get(check_id)

        assert res.status_code == 200
        assert check_user.temporary_token is not None
        assert app.notify_message is not None
        assert check_user.temporary_token in app.notify_message.as_string()
        assert app.notify_message["Subject"] == "Reset Password"
        assert app.notify_message["From"] == app.config.get("EMAIL_SENDER_ADDRESS")
        assert app.notify_message["To"] == check_email

    def test_get_reset_password_token_not_valid(self, db: DBConfig, client: FlaskClient, reset_password_user: User) -> None:
        res = client.get(
            "/api/v1/users/reset-password/123123123213",
        )
        assert res.status_code == 404

    def test_get_reset_password_token_valid(self, db: DBConfig, client: FlaskClient, reset_password_user: User) -> None:
        res = client.get(
            f"/api/v1/users/reset-password/{reset_password_user.temporary_token}",
        )
        assert res.status_code == 200

    def test_reset_password_patch_token_not_valid(self, db: DBConfig, client: FlaskClient, reset_password_user: User) -> None:
        json = {"password": "test_valid"}
        res = client.patch("/api/v1/users/reset-password/12312312312123", json=json)
        assert res.status_code == 404

    def test_reset_password_password_not_valid(self, db: DBConfig, client: FlaskClient, reset_password_user: User) -> None:
        json = {"password": ""}
        res = client.patch(
            f"/api/v1/users/reset-password/{reset_password_user.temporary_token}",
            json=json,
        )
        assert res.status_code == 422

    def test_reset_password_valid(self, db: DBConfig, client: FlaskClient, reset_password_user: User) -> None:
        check_id = reset_password_user.id
        last_password_update = reset_password_user.last_password_update

        json = {"password": "test_valid@Test10"}
        res = client.patch(
            f"/api/v1/users/reset-password/{reset_password_user.temporary_token}",
            json=json,
        )

        check_user = User.get(check_id)
        assert res.status_code == 200
        assert check_user.check_password("test_valid@Test10")
        assert check_user.last_password_update != last_password_update


class TestUserChangePasswordActions:
    def test_user_change_password_fail_no_data(
        self,
        db: DBConfig,
        client: FlaskClient,
        regular_user: User,
        regular_user_headers: Mapping[str, str],
    ) -> None:

        data: dict[str, str] = {}
        response = client.post("/api/v1/users/change-password", headers=regular_user_headers, json=data)

        errors = response.get_json()
        assert errors
        assert len(errors) == 3
        assert response.status_code == 422

    def test_user_change_password_fail_no_old_password(
        self,
        db: DBConfig,
        client: FlaskClient,
        regular_user: User,
        regular_user_headers: Mapping[str, str],
    ) -> None:

        data: dict[str, str] = {
            "old_password": "",
            "new_password": "test_valid@Test10",
            "new_password_confirm": "test_valid@Test10",
        }

        response = client.post("/api/v1/users/change-password", headers=regular_user_headers, json=data)

        errors = response.get_json()

        assert errors
        assert "old_password" in errors.keys()
        assert "Old Password must not be empty" in errors["old_password"]
        assert len(errors) == 1
        assert response.status_code == 422

    def test_user_change_password_fail_wrong_old_password(
        self,
        db: DBConfig,
        client: FlaskClient,
        regular_user: User,
        regular_user_headers: Mapping[str, str],
    ) -> None:

        data: dict[str, str] = {
            "old_password": "tes",
            "new_password": "test_valid@Test10",
            "new_password_confirm": "test_valid@Test10",
        }

        response = client.post("/api/v1/users/change-password", headers=regular_user_headers, json=data)

        errors = response.get_json()

        assert errors
        assert "old_password" in errors.keys()
        assert "Wrong old password" in errors["old_password"]
        assert len(errors) == 1
        assert response.status_code == 422

    def test_user_change_password_fail_password_mismatch(
        self,
        db: DBConfig,
        client: FlaskClient,
        regular_user: User,
        regular_user_headers: Mapping[str, str],
    ) -> None:

        data: dict[str, str] = {
            "old_password": "test",
            "new_password": "test_valid@Test10",
            "new_password_confirm": "pass",
        }

        response = client.post("/api/v1/users/change-password", headers=regular_user_headers, json=data)

        errors = response.get_json()

        assert errors
        assert "passwords" in errors.keys()
        assert "Passwords are not the same" in errors["passwords"]
        assert len(errors) == 1
        assert response.status_code == 422

    def test_user_change_password_fail_empty_new_password(
        self,
        db: DBConfig,
        client: FlaskClient,
        regular_user: User,
        regular_user_headers: Mapping[str, str],
    ) -> None:

        data = {
            "old_password": "test",
            "new_password": "",
            "new_password_confirm": "",
        }

        response = client.post("/api/v1/users/change-password", headers=regular_user_headers, json=data)

        errors = response.get_json()
        assert errors
        assert "new_password" in errors.keys()
        assert "Password must not be empty" in errors["new_password"]
        assert len(errors) == 1
        assert response.status_code == 422

    def test_user_change_password_201(
        self,
        db: DBConfig,
        client: FlaskClient,
        regular_user: User,
        regular_user_headers: Mapping[str, str],
    ) -> None:

        user_id = regular_user.id
        last_password_update = regular_user.last_password_update

        data = {
            "old_password": "test",
            "new_password": "test_valid@Test10",
            "new_password_confirm": "test_valid@Test10",
        }

        response = client.post("/api/v1/users/change-password", headers=regular_user_headers, json=data)

        result = response.get_json()

        updated_user = User.get(user_id)

        assert updated_user.last_password_update != last_password_update
        assert updated_user.id == user_id
        assert result
        assert "message" in result.keys()
        assert "password updated" in result["message"]
        assert updated_user.check_password("test_valid@Test10")
        assert response.status_code == 201

    def test_base_user_change_password_201(
        self,
        db: DBConfig,
        client: FlaskClient,
        regular_user: User,
        regular_user_headers: Mapping[str, str],
    ) -> None:

        user_id = regular_user.id
        last_password_update = regular_user.last_password_update

        data = {
            "old_password": "test",
            "new_password": "test_valid@Test10",
            "new_password_confirm": "test_valid@Test10",
        }

        response = client.post("/api/v1/users/change-password", headers=regular_user_headers, json=data)

        result = response.get_json()

        updated_user = User.get(user_id)

        assert updated_user.last_password_update != last_password_update
        assert updated_user.id == user_id
        assert result
        assert "message" in result.keys()
        assert "password updated" in result["message"]
        assert updated_user.check_password("test_valid@Test10")
        assert response.status_code == 201
