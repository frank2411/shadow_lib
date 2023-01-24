import uuid
from typing import Mapping

from flask.testing import FlaskClient

from shadow_lib.models import AUTHOR_NOT_FOUND_ERR_MESSAGE, Author, User
from shadow_lib.models.db import DBConfig


class TestAuthorDetailRetrieve:
    def test_get_author_success(
        self,
        db: DBConfig,
        client: FlaskClient,
        simple_author: Author,
        regular_user_headers: Mapping[str, str],
    ) -> None:

        res = client.get(f"/api/v1/authors/{simple_author.id}", headers=regular_user_headers)

        assert res.status_code == 200
        assert res.json
        assert res.json["author"]["id"] == str(simple_author.id)

    def test_get_author_not_found(
        self,
        db: DBConfig,
        client: FlaskClient,
        random_uuid: uuid.UUID,
        regular_user_headers: Mapping[str, str],
    ) -> None:

        res = client.get(f"/api/v1/authors/{random_uuid}", headers=regular_user_headers)

        assert res.status_code == 404
        assert res.json
        assert res.json["message"] == AUTHOR_NOT_FOUND_ERR_MESSAGE


class TestAuthorDetailGetAndUpdateAndDelete:
    def test_update_author(
        self,
        db: DBConfig,
        client: FlaskClient,
        simple_author: Author,
        regular_user_headers: Mapping[str, str],
    ) -> None:

        data = {
            "first_name": "another test"
        }

        res = client.patch(f"/api/v1/authors/{simple_author.id}", json=data, headers=regular_user_headers)

        assert res.status_code == 200
        assert res.json
        assert res.json["author"]["id"] == str(simple_author.id)
        assert res.json["author"]["first_name"] == data["first_name"]

    def test_update_author_fail_unkown_field(
        self,
        db: DBConfig,
        client: FlaskClient,
        simple_author: Author,
        regular_user_headers: Mapping[str, str],
    ) -> None:

        data = {
            "books": ["wetry"]
        }

        res = client.patch(f"/api/v1/authors/{simple_author.id}", json=data, headers=regular_user_headers)

        assert res.status_code == 422
        assert res.json
        assert res.json["books"][0] == "Unknown field."

    def test_delete_author_success(
        self,
        db: DBConfig,
        client: FlaskClient,
        simple_author: Author,
        regular_user_headers: Mapping[str, str],
    ) -> None:

        res = client.delete(f"/api/v1/authors/{simple_author.id}", headers=regular_user_headers)

        assert res.status_code == 200
        assert res.json["message"] == "author deleted"

    def test_delete_author_fail_author_not_found(
        self,
        db: DBConfig,
        client: FlaskClient,
        random_uuid: uuid.UUID,
        regular_user_headers: Mapping[str, str],
    ) -> None:

        res = client.delete(f"/api/v1/authors/{random_uuid}", headers=regular_user_headers)

        assert res.status_code == 404
        assert res.json["message"] == "Author not found"


class TestAuthorListAndCreation:
    def test_create_author_success(
        self,
        db: DBConfig,
        client: FlaskClient,
        regular_user: User,
        regular_user_headers: Mapping[str, str],
    ):

        data = dict(
            first_name="test",
            last_name="test",
        )

        res = client.post("/api/v1/authors", json=data, headers=regular_user_headers)

        assert res.status_code == 201
        assert res.json["message"] == "author created"
        assert res.json["author"]["created_by"] == str(regular_user.id)

    def test_create_author_error_empty_first_name(
        self,
        db: DBConfig,
        client: FlaskClient,
        regular_user_headers: Mapping[str, str],
    ):

        data = dict(
            last_name="test",
        )

        res = client.post("/api/v1/authors", json=data, headers=regular_user_headers)

        assert res.status_code == 422
        assert res.json["first_name"][0] == "Missing data for required field."

    def test_get_authors_success(
        self,
        db: DBConfig,
        client: FlaskClient,
        simple_author: Author,
        superadmin_headers: Mapping[str, str],
    ) -> None:

        res = client.get("/api/v1/authors", headers=superadmin_headers)

        assert res.status_code == 200
        assert len(res.json["authors"]) == 1
