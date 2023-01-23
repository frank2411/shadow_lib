import uuid
from typing import Any, Dict, Mapping, cast

from flask.testing import FlaskClient

from shadow_lib.models.user import UserRoles
from shadow_lib.models import USER_NOT_FOUND_ERR_MESSAGE, User
from shadow_lib.models.db import DBConfig


class TestUserDetailRetrieve:
    def test_get_user_as_superadmin_success(
        self,
        db: DBConfig,
        client: FlaskClient,
        regular_user: User,
        superadmin: User,
        superadmin_headers: Mapping[str, str],
    ) -> None:

        res = client.get(f"/api/v1/users/{regular_user.id}", headers=superadmin_headers)

        assert res.status_code == 200
        assert res.json
        assert res.json["user"]["email"] == regular_user.email

    def test_get_user_regular_user_403(
        self,
        client: FlaskClient,
        db: DBConfig,
        regular_user_headers: Mapping[str, str],
        regular_user: User,
        random_uuid: uuid.UUID,
    ) -> None:

        res = client.get(f"/api/v1/users/{random_uuid}", headers=regular_user_headers)
        assert res.status_code == 403

    def test_get_users_get_me(
        self,
        client: FlaskClient,
        db: DBConfig,
        regular_user_headers: Mapping[str, str],
        regular_user: User,
    ) -> None:

        res = client.get("/api/v1/users/me", headers=regular_user_headers)

        res_json = res.get_json()

        assert res.status_code == 200
        assert res_json
        assert res_json["me"]["id"] == str(regular_user.id)
        assert res_json["me"]["email"] == regular_user.email
        assert "password" not in res_json["me"]


class TestUserDetailGetAndUpdateAndDelete:
    def test_update_user_me(
        self,
        client: FlaskClient,
        db: DBConfig,
        superadmin_headers: Mapping[str, str],
        superadmin: User,
    ) -> None:
        data = {
            "email": "test_email@email.com",
        }

        res = client.patch(f"/api/v1/users/{superadmin.id}", headers=superadmin_headers, json=data)

        assert res.status_code == 200
        assert res.json
        assert res.json["user"]["email"] == data["email"]

    def test_update_user_regular_user_403(
        self,
        client: FlaskClient,
        db: DBConfig,
        regular_user_headers: Mapping[str, str],
        regular_user: User,
        random_uuid: uuid.UUID,
    ) -> None:
        data = {
            "email": "test_email@email.com",
        }

        res = client.patch(f"/api/v1/users/{random_uuid}", headers=regular_user_headers, json=data)
        assert res.status_code == 403

    def test_update_user_superadmin_success(
        self,
        db: DBConfig,
        client: FlaskClient,
        superadmin_headers: Mapping[str, str],
        regular_user: User,
        superadmin: User,
        # organization: Organization,
        # group: Group,
    ) -> None:
        data = {
            "email": "new@email.it",
            # "organization": organization.id,
            # "groups": [group.id],
            "password": "new_password",
        }

        res = client.patch(f"/api/v1/users/{regular_user.id}", headers=superadmin_headers, json=data)

        assert res.status_code == 200
        assert res.json
        assert res.json["user"]["id"] == str(regular_user.id)
        assert res.json["user"]["email"] == data["email"]
        # assert res.json["user"]["organization"]["id"] == str(data["organization"])
        # assert res.json["user"]["groups"][0]["id"] == str(data["groups"][0])

    def test_update_user_superadmin_error(
        self,
        db: DBConfig,
        client: FlaskClient,
        superadmin_headers: Mapping[str, str],
        regular_user: User,
        superadmin: User,
        # organization: Organization,
        # group: Group,
    ) -> None:
        data = {
            "email": "",
            # "organization": organization.id,
            # "groups": [group.id],
        }

        res = client.patch(f"/api/v1/users/{regular_user.id}", headers=superadmin_headers, json=data)
        res_json = res.get_json()

        assert res.status_code == 422
        assert res_json
        assert res_json["email"][0] == "Not a valid email address."

    def test_delete_user_as_superadmin_success(
        self,
        db: DBConfig,
        client: FlaskClient,
        regular_user: User,
        superadmin: User,
        superadmin_headers: Mapping[str, str],
    ) -> None:

        res = client.delete(f"/api/v1/users/{regular_user.id}", headers=superadmin_headers)

        assert res.status_code == 200
        assert res.json
        assert res.json["message"] == "user deleted"

    def test_delete_user_as_superadmin_404(
        self,
        db: DBConfig,
        client: FlaskClient,
        regular_user: User,
        superadmin: User,
        superadmin_headers: Mapping[str, str],
        random_uuid: uuid.UUID,
    ) -> None:

        res = client.delete(f"/api/v1/users/{random_uuid}", headers=superadmin_headers)
        assert res.status_code == 404
        assert cast(Mapping[str, Any], res.json)["message"] == USER_NOT_FOUND_ERR_MESSAGE

    def test_delete_user_as_regular_403(
        self,
        db: DBConfig,
        client: FlaskClient,
        regular_user: User,
        superadmin: User,
        regular_user_headers: Mapping[str, str],
        random_uuid: uuid.UUID,
    ) -> None:

        res = client.delete(f"/api/v1/users/{random_uuid}", headers=regular_user_headers)
        assert res.status_code == 403


class TestUserListAndCreation:
    def test_get_users_as_regular_403(
        self,
        db: DBConfig,
        client: FlaskClient,
        regular_user: User,
        superadmin: User,
        regular_user_headers: Mapping[str, str],
    ) -> None:

        res = client.get("/api/v1/users", headers=regular_user_headers)

        assert res.status_code == 403

    def test_get_users_as_superadmin_success(
        self,
        db: DBConfig,
        client: FlaskClient,
        regular_user: User,
        superadmin: User,
        superadmin_headers: Mapping[str, str],
    ) -> None:

        res = client.get("/api/v1/users", headers=superadmin_headers)

        assert res.status_code == 200
        assert len(cast(Mapping[str, Any], res.json)["users"]) == 2

    def test_create_user_as_regular_403(
        self,
        db: DBConfig,
        client: FlaskClient,
        regular_user: User,
        superadmin: User,
        regular_user_headers: Mapping[str, str],
    ) -> None:

        data = {"nodata": "nodata"}
        res = client.post("/api/v1/users", headers=regular_user_headers, json=data)

        assert res.status_code == 403

    def test_create_user_as_superadmin_regular_user_success(
        self,
        db: DBConfig,
        client: FlaskClient,
        superadmin: User,
        superadmin_headers: Mapping[str, str],
    ) -> None:

        data = {
            "email": "an@email.com",
            "password": "apassword",
        }
        res = client.post("/api/v1/users", headers=superadmin_headers, json=data)

        res_json = res.get_json()

        assert res.status_code == 201
        assert res_json
        assert res_json["user"]["role"] == UserRoles.user.value
        assert res_json["user"]["email"] == data["email"]

    def test_create_user_as_superadmin_regular_user_existing_email_fail(
        self,
        db: DBConfig,
        client: FlaskClient,
        superadmin: User,
        superadmin_headers: Mapping[str, str],
    ) -> None:
        data = {
            "email": superadmin.email,
            "password": "apassword",
        }
        res = client.post("/api/v1/users", headers=superadmin_headers, json=data)

        res_json = res.get_json()

        assert res.status_code == 422
        assert res_json["email"][0] == "Email already exists"

    def test_create_user_as_superadmin_superadmin_success(
        self,
        db: DBConfig,
        client: FlaskClient,
        superadmin: User,
        superadmin_headers: Mapping[str, str],
    ) -> None:

        data = {
            "email": "an@email.com",
            "password": "apassword",
            "role": "superadmin",
        }
        res = client.post("/api/v1/users", headers=superadmin_headers, json=data)

        res_json = res.get_json()

        assert res.status_code == 201
        assert res_json
        assert res_json["user"]["role"] == UserRoles.superadmin
        assert res_json["user"]["email"] == data["email"]

    def test_create_user_as_superadmin_bad_role_error(
        self,
        db: DBConfig,
        client: FlaskClient,
        superadmin: User,
        superadmin_headers: Mapping[str, str],
    ) -> None:

        data = {
            "email": "an@email.com",
            "password": "apassword",
            "role": "notexistingrole",
        }
        res = client.post("/api/v1/users", headers=superadmin_headers, json=data)

        res_json = res.get_json()

        assert res.status_code == 422
        assert res_json
        assert "Role does not exist" in res_json["role"]
