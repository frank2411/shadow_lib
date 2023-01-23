from flask.testing import FlaskClient

from shadow_lib.models import User
from shadow_lib.models.db import DBConfig


class TestLogin:
    def test_login_no_json(self, client: FlaskClient) -> None:
        res = client.post("/api/v1/login")
        res_json = res.get_json()

        assert res.status_code == 400
        assert res_json
        assert res_json["message"] == "Missing JSON in request"

    def test_login_no_credentials(self, client: FlaskClient) -> None:
        res = client.post("/api/v1/login", json={})
        res_json = res.get_json()

        assert res.status_code == 400
        assert res_json
        assert res_json["message"] == "Missing credentials"

    def test_login_no_email(self, client: FlaskClient) -> None:
        res = client.post("/api/v1/login", json={"password": "test"})
        res_json = res.get_json()

        assert res.status_code == 400
        assert res_json
        assert res_json["message"] == "Missing credentials"

    def test_login_no_password(self, client: FlaskClient) -> None:
        res = client.post("/api/v1/login", json={"email": "test@email.com"})
        res_json = res.get_json()

        assert res.status_code == 400
        assert res_json
        assert res_json["message"] == "Missing credentials"

    def test_login_wrong_password(self, client: FlaskClient, regular_user: User) -> None:
        data = {"email": regular_user.email, "password": "test2222"}
        res = client.post("/api/v1/login", json=data)
        res_json = res.get_json()

        assert res.status_code == 400
        assert res_json
        assert res_json["message"] == "No account with these credentials"

    def test_login_wrong_email(self, client: FlaskClient, regular_user: User) -> None:
        data = {"email": "no@email.com", "password": "test2222"}
        res = client.post("/api/v1/login", json=data)
        res_json = res.get_json()

        assert res.status_code == 400
        assert res_json
        assert res_json["message"] == "No account with these credentials"

    def test_login_success(self, client: FlaskClient, regular_user: User) -> None:

        old_last_login_date = regular_user.last_login_date

        data = {"email": regular_user.email, "password": "test"}
        res = client.post("/api/v1/login", json=data)
        res_json = res.get_json()

        user_to_check_date = User.get(regular_user.id)
        user_to_check_date = user_to_check_date.last_login_date

        assert res.status_code == 200
        assert res_json
        assert "access_token" in res_json
        assert "refresh_token" in res_json
        assert user_to_check_date > old_last_login_date


class TestDecoratorAuthorization:
    def test_get_user_not_authorized(
        self,
        db: DBConfig,
        client: FlaskClient,
        regular_user: User,
        regular_user_headers: dict[str, str],
    ) -> None:
        res = client.get(f"/api/v1/users/{regular_user.id}", headers=regular_user_headers)

        res_json = res.get_json()

        assert res.status_code == 403
        assert res_json
        assert res_json["message"] == "Access forbidden"

    def test_update_user_not_authorized(
        self,
        db: DBConfig,
        client: FlaskClient,
        regular_user: User,
        regular_user_headers: dict[str, str],
    ) -> None:
        res = client.patch(f"/api/v1/users/{regular_user.id}", headers=regular_user_headers)

        res_json = res.get_json()

        assert res.status_code == 403
        assert res_json
        assert res_json["message"] == "Access forbidden"
