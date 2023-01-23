import uuid
from typing import Mapping

from flask.testing import FlaskClient

from shadow_lib.models import BORROWED_BOOK_NOT_FOUND_ERR_MESSAGE, User, Book
from shadow_lib.models import Order
from shadow_lib.models.db import DBConfig


class TestBorrowedBookDetailRetrieve:
    def test_get_borrowed_book_success(
        self,
        db: DBConfig,
        client: FlaskClient,
        simple_order: Order,
        regular_user_headers: Mapping[str, str],
    ) -> None:

        res = client.get(f"/api/v1/borrowed-books/{simple_order.borrowed_books[0].id}", headers=regular_user_headers)

        assert res.status_code == 200
        assert res.json
        assert res.json["borrowed_book"]["id"] == str(simple_order.borrowed_books[0].id)
        assert res.json["borrowed_book"]["book_id"] == str(simple_order.borrowed_books[0].book_id)
        assert res.json["borrowed_book"]["order_id"] == str(simple_order.borrowed_books[0].order_id)

    def test_get_borrowed_book_not_found(
        self,
        db: DBConfig,
        client: FlaskClient,
        random_uuid: uuid.UUID,
        regular_user_headers: Mapping[str, str],
    ) -> None:

        res = client.get(f"/api/v1/borrowed-books/{random_uuid}", headers=regular_user_headers)

        assert res.status_code == 404
        assert res.json
        assert res.json["message"] == BORROWED_BOOK_NOT_FOUND_ERR_MESSAGE


class TestBorrowedBookDetailGetAndUpdateAndDelete:

    def test_update_borrowed_book_success_with_quantity_update(
        self,
        db: DBConfig,
        client: FlaskClient,
        regular_user: User,
        simple_book: Book,
        simple_order: Order,
        regular_user_headers: Mapping[str, str],
    ) -> None:

        original_qty = simple_book.qty - simple_order.borrowed_books[0].qty
        original_borrowed_qty = simple_order.borrowed_books[0].qty

        assert original_qty == 16

        simple_book.qty = original_qty
        simple_book.save()

        data = dict(
            qty=12
        )

        res = client.patch(f"/api/v1/borrowed-books/{simple_order.borrowed_books[0].id}", json=data, headers=regular_user_headers)

        assert res.status_code == 200
        assert res.json
        assert res.json["borrowed_book"]["order_id"] == str(simple_order.id)
        assert res.json["borrowed_book"]["book_id"] == str(simple_book.id)
        assert res.json["borrowed_book"]["qty"] == 12

        updated_qty_check = Book.get(simple_book.id).qty

        assert original_qty != updated_qty_check
        assert updated_qty_check == ((original_qty + original_borrowed_qty) - 12)

    def test_update_borrowed_book_error_exceeding_quantity(
        self,
        db: DBConfig,
        client: FlaskClient,
        regular_user: User,
        simple_book: Book,
        simple_order: Order,
        regular_user_headers: Mapping[str, str],
    ) -> None:

        original_qty = simple_book.qty - simple_order.borrowed_books[0].qty

        assert original_qty == 16

        simple_book.qty = original_qty
        simple_book.save()

        data = dict(
            qty=1000
        )

        res = client.patch(f"/api/v1/borrowed-books/{simple_order.borrowed_books[0].id}", json=data, headers=regular_user_headers)

        assert res.status_code == 422
        assert res.json
        assert res.json["book"][0] == f"Quantity for this book {simple_book.id} is too much"

    def test_update_borrowed_book_no_change_in_quantity_changed_order_id(
        self,
        db: DBConfig,
        client: FlaskClient,
        regular_user: User,
        simple_book: Book,
        simple_order: Order,
        simple_order_2_books: Order,
        regular_user_headers: Mapping[str, str],
    ) -> None:

        original_qty = simple_book.qty - simple_order.borrowed_books[0].qty

        assert original_qty == 16

        simple_book.qty = original_qty
        simple_book.save()

        data = dict(
            order_id=str(simple_order_2_books.id),
        )

        res = client.patch(f"/api/v1/borrowed-books/{simple_order.borrowed_books[0].id}", json=data, headers=regular_user_headers)

        assert res.status_code == 200
        assert res.json
        assert res.json["borrowed_book"]["order_id"] == str(simple_order_2_books.id)
        assert res.json["borrowed_book"]["book_id"] == str(simple_book.id)
        assert res.json["borrowed_book"]["qty"] == simple_order_2_books.borrowed_books[0].qty

        updated_qty_check = Book.get(simple_book.id).qty

        assert original_qty == updated_qty_check

    def test_update_borrowed_book_inexistent_order_id(
        self,
        db: DBConfig,
        client: FlaskClient,
        regular_user: User,
        random_uuid: uuid.UUID,
        simple_order: Order,
        simple_order_2_books: Order,
        regular_user_headers: Mapping[str, str],
    ) -> None:

        data = dict(
            order_id=str(random_uuid),
        )

        res = client.patch(f"/api/v1/borrowed-books/{simple_order.borrowed_books[0].id}", json=data, headers=regular_user_headers)

        assert res.status_code == 422
        assert res.json
        assert res.json["order_id"][0] == "Related Object doesn't exist in DB"

    def test_delete_borrowed_book_success(
        self,
        db: DBConfig,
        client: FlaskClient,
        regular_user: User,
        simple_book: Book,
        simple_order: Order,
        regular_user_headers: Mapping[str, str],
    ) -> None:

        original_qty = simple_book.qty - simple_order.borrowed_books[0].qty
        original_borrowed_qty = simple_order.borrowed_books[0].qty

        assert original_qty == 16

        simple_book.qty = original_qty
        simple_book.save()

        res = client.delete(f"/api/v1/borrowed-books/{simple_order.borrowed_books[0].id}", headers=regular_user_headers)

        assert res.status_code == 200
        assert res.json
        assert res.json["message"] == "borrowed book deleted"

        updated_qty_check = Book.get(simple_book.id).qty

        assert original_qty != updated_qty_check
        assert updated_qty_check == (original_qty + original_borrowed_qty)

    def test_delete_borrowed_book_error_not_found(
        self,
        db: DBConfig,
        client: FlaskClient,
        regular_user: User,
        random_uuid: uuid.UUID,
        regular_user_headers: Mapping[str, str],
    ) -> None:

        res = client.delete(f"/api/v1/borrowed-books/{random_uuid}", headers=regular_user_headers)

        assert res.status_code == 404
        assert res.json
        assert res.json["message"] == BORROWED_BOOK_NOT_FOUND_ERR_MESSAGE


class TestBorrowedBookListAndCreation:

    def test_create_borrowed_book_success(
        self,
        db: DBConfig,
        client: FlaskClient,
        simple_order: Order,
        simple_book_2: Order,
        regular_user_headers: Mapping[str, str],
    ) -> None:

        data = dict(
            order_id=str(simple_order.id),
            book_id=str(simple_book_2.id),
            qty=8
        )

        original_qty = simple_book_2.qty

        res = client.post("/api/v1/borrowed-books", json=data, headers=regular_user_headers)

        updated_qty = Book.get(simple_book_2.id).qty

        assert res.status_code == 201
        assert (original_qty - 8) == updated_qty

    def test_create_borrowed_book_error_exceeding_quantity(
        self,
        db: DBConfig,
        client: FlaskClient,
        simple_order: Order,
        simple_book_2: Order,
        regular_user_headers: Mapping[str, str],
    ) -> None:

        data = dict(
            order_id=str(simple_order.id),
            book_id=str(simple_book_2.id),
            qty=8000
        )

        res = client.post("/api/v1/borrowed-books", json=data, headers=regular_user_headers)

        assert res.status_code == 422
        assert res.json
        assert res.json["book"][0] == f"Quantity for this book {simple_book_2.id} is too much"

    def test_get_borrowed_books_success(
        self,
        db: DBConfig,
        client: FlaskClient,
        simple_order: Order,
        simple_order_2_books: Order,
        regular_user_headers: Mapping[str, str],
    ) -> None:

        res = client.get("/api/v1/borrowed-books", headers=regular_user_headers)

        assert res.status_code == 200
        assert len(res.json["borrowed_books"]) == 3
