import uuid
from typing import Mapping

from flask.testing import FlaskClient

from shadow_lib.models import BOOK_NOT_FOUND_ERR_MESSAGE, Book, User, Author
from shadow_lib.models.db import DBConfig


class TestBookDetailRetrieve:
    def test_get_book_success(
        self,
        db: DBConfig,
        client: FlaskClient,
        simple_book: Book,
        regular_user_headers: Mapping[str, str],
    ) -> None:

        res = client.get(f"/api/v1/books/{simple_book.id}", headers=regular_user_headers)

        assert res.status_code == 200
        assert res.json
        assert res.json["book"]["id"] == str(simple_book.id)
        assert res.json["book"]["authors"][0] == str(simple_book.authors[0].id)

    def test_get_book_not_found(
        self,
        db: DBConfig,
        client: FlaskClient,
        random_uuid: uuid.UUID,
        regular_user_headers: Mapping[str, str],
    ) -> None:

        res = client.get(f"/api/v1/books/{random_uuid}", headers=regular_user_headers)

        assert res.status_code == 404
        assert res.json
        assert res.json["message"] == BOOK_NOT_FOUND_ERR_MESSAGE


class TestBookDetailGetAndUpdateAndDelete:

    def test_update_book(
        self,
        db: DBConfig,
        client: FlaskClient,
        simple_book: Book,
        regular_user_headers: Mapping[str, str],
    ) -> None:

        data = {
            "title": "another test"
        }

        res = client.patch(f"/api/v1/books/{simple_book.id}", json=data, headers=regular_user_headers)

        assert res.status_code == 200
        assert res.json
        assert res.json["book"]["id"] == str(simple_book.id)
        assert res.json["book"]["title"] == data["title"]

    def test_update_book_fail_empty_authors(
        self,
        db: DBConfig,
        client: FlaskClient,
        simple_book: Book,
        regular_user_headers: Mapping[str, str],
    ) -> None:

        data = {
            "authors": []
        }

        res = client.patch(f"/api/v1/books/{simple_book.id}", json=data, headers=regular_user_headers)

        assert res.status_code == 422
        assert res.json
        assert res.json["authors"][0] == "Authors value cannot be empty."

    def test_delete_book_success(
        self,
        db: DBConfig,
        client: FlaskClient,
        simple_book: Book,
        regular_user_headers: Mapping[str, str],
    ) -> None:

        res = client.delete(f"/api/v1/books/{simple_book.id}", headers=regular_user_headers)

        assert res.status_code == 200
        assert res.json["message"] == "book deleted"

    def test_delete_book_fail_author_not_found(
        self,
        db: DBConfig,
        client: FlaskClient,
        random_uuid: uuid.UUID,
        regular_user_headers: Mapping[str, str],
    ) -> None:

        res = client.delete(f"/api/v1/books/{random_uuid}", headers=regular_user_headers)

        assert res.status_code == 404
        assert res.json["message"] == "Book not found"


class TestBookListAndCreation:
    def test_create_book_success(
        self,
        db: DBConfig,
        client: FlaskClient,
        simple_author: Author,
        regular_user: User,
        regular_user_headers: Mapping[str, str],
    ):

        data = dict(
            title="test",
            EAN="test",
            SKU="TEST",
            release_date="2022-10-10",
            qty=20,
            authors=[str(simple_author.id)]
        )

        res = client.post("/api/v1/books", json=data, headers=regular_user_headers)

        assert res.status_code == 201
        assert res.json["message"] == "book created"
        assert res.json["book"]["created_by"] == str(regular_user.id)

    def test_create_book_error_empty_authors(
        self,
        db: DBConfig,
        client: FlaskClient,
        regular_user_headers: Mapping[str, str],
    ):

        data = dict(
            title="test",
            EAN="test",
            SKU="TEST",
            release_date="2022-10-10",
            qty=20,
        )

        res = client.post("/api/v1/books", json=data, headers=regular_user_headers)

        assert res.status_code == 422
        assert res.json["authors"][0] == "Missing data for required field."

    def test_get_books_success(
        self,
        db: DBConfig,
        client: FlaskClient,
        simple_book: Book,
        superadmin_headers: Mapping[str, str],
    ) -> None:

        res = client.get("/api/v1/books", headers=superadmin_headers)

        assert res.status_code == 200
        assert len(res.json["books"]) == 1
