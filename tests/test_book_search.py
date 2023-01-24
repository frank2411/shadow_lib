# import uuid
from typing import Mapping

from flask.testing import FlaskClient

from shadow_lib.models import Book, Author
from shadow_lib.models.db import DBConfig


class TestBookDetailRetrieve:
    def test_get_book_success_no_results(
        self,
        db: DBConfig,
        client: FlaskClient,
        simple_book: Book,
        simple_book_2: Book,
        regular_user_headers: Mapping[str, str],
    ) -> None:

        res = client.get(
            "/api/v1/books/search?q=asdasdasdassasdd",
            headers=regular_user_headers
        )

        assert res.status_code == 200
        assert res.json
        assert res.json["books"] == []

    def test_get_book_success_all_results(
        self,
        db: DBConfig,
        client: FlaskClient,
        simple_book: Book,
        simple_book_2: Book,
        regular_user_headers: Mapping[str, str],
    ) -> None:

        res = client.get(
            "/api/v1/books/search?q=test",
            headers=regular_user_headers
        )

        assert res.status_code == 200
        assert res.json
        assert len(res.json["books"]) == 2

    def test_get_book_success_results_by_author(
        self,
        db: DBConfig,
        client: FlaskClient,
        simple_book: Book,
        simple_book_2: Book,
        simple_book_3: Book,
        simple_author: Author,
        simple_author_2: Author,
        regular_user_headers: Mapping[str, str],
    ) -> None:

        res = client.get(
            "/api/v1/books/search?q=viam",
            headers=regular_user_headers
        )

        assert res.status_code == 200
        assert res.json
        assert len(res.json["books"]) == 1

    def test_get_book_no_q_filter(
        self,
        db: DBConfig,
        client: FlaskClient,
        simple_book: Book,
        simple_book_2: Book,
        simple_book_3: Book,
        simple_author: Author,
        simple_author_2: Author,
        regular_user_headers: Mapping[str, str],
    ) -> None:

        res = client.get(
            "/api/v1/books/search",
            headers=regular_user_headers
        )

        assert res.status_code == 422
        assert res.json
        assert res.json["q"][0] == 'Missing data for required field.'

    def test_get_book_q_filter_empty_string(
        self,
        db: DBConfig,
        client: FlaskClient,
        simple_book: Book,
        simple_book_2: Book,
        simple_book_3: Book,
        simple_author: Author,
        simple_author_2: Author,
        regular_user_headers: Mapping[str, str],
    ) -> None:

        res = client.get(
            "/api/v1/books/search?q=",
            headers=regular_user_headers
        )

        assert res.status_code == 422
        assert res.json
        assert res.json["q"][0] == 'Shorter than minimum length 1.'
