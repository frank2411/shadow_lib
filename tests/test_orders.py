import uuid
from typing import Mapping

from flask.testing import FlaskClient

from shadow_lib.models import ORDER_NOT_FOUND_ERR_MESSAGE, Customer, User, Book
from shadow_lib.models import Order
from shadow_lib.models.db import DBConfig


class TestOrderDetailRetrieve:
    def test_get_order_success(
        self,
        db: DBConfig,
        client: FlaskClient,
        simple_order: Order,
        regular_user_headers: Mapping[str, str],
    ) -> None:

        res = client.get(f"/api/v1/orders/{simple_order.id}", headers=regular_user_headers)

        assert res.status_code == 200
        assert res.json
        assert res.json["order"]["id"] == str(simple_order.id)
        assert len(res.json["order"]["borrowed_books"]) == 1

    def test_get_book_not_found(
        self,
        db: DBConfig,
        client: FlaskClient,
        random_uuid: uuid.UUID,
        regular_user_headers: Mapping[str, str],
    ) -> None:

        res = client.get(f"/api/v1/orders/{random_uuid}", headers=regular_user_headers)

        assert res.status_code == 404
        assert res.json
        assert res.json["message"] == ORDER_NOT_FOUND_ERR_MESSAGE


class TestOrderDetailGetAndUpdateAndDelete:
    def test_update_order(
        self,
        db: DBConfig,
        client: FlaskClient,
        simple_order: Order,
        simple_book: Book,
        simple_customer_2: Customer,
        regular_user_headers: Mapping[str, str],
    ) -> None:

        data = dict(
            customer=str(simple_customer_2.id)
        )

        assert simple_order.customer_id != simple_customer_2.id

        res = client.patch(f"/api/v1/orders/{simple_order.id}", json=data, headers=regular_user_headers)

        assert res.status_code == 200
        assert res.json
        assert res.json["order"]["id"] == str(simple_order.id)
        assert res.json["order"]["customer"] == str(simple_customer_2.id)
        assert "borrowed_books" not in res.json["order"]

    def test_update_order_error_trying_to_modify_borrowed_books(
        self,
        db: DBConfig,
        client: FlaskClient,
        simple_order: Order,
        simple_book: Book,
        simple_customer_2: Customer,
        regular_user_headers: Mapping[str, str],
    ) -> None:

        data = dict(
            borrowed_books=[
                dict(
                    book_id=str(simple_book.id),
                    qty=12
                )
            ]
        )

        res = client.patch(f"/api/v1/orders/{simple_order.id}", json=data, headers=regular_user_headers)

        assert res.status_code == 422
        assert res.json
        assert res.json["borrowed_books"][0] == "Unknown field."

    def test_delete_order_success(
        self,
        db: DBConfig,
        client: FlaskClient,
        simple_order: Customer,
        regular_user_headers: Mapping[str, str],
    ) -> None:

        res = client.delete(f"/api/v1/orders/{simple_order.id}", headers=regular_user_headers)

        assert res.status_code == 200
        assert res.json["message"] == "order deleted"

    def test_delete_customer_fail_customer_not_found(
        self,
        db: DBConfig,
        client: FlaskClient,
        random_uuid: uuid.UUID,
        regular_user_headers: Mapping[str, str],
    ) -> None:

        res = client.delete(f"/api/v1/orders/{random_uuid}", headers=regular_user_headers)

        assert res.status_code == 404
        assert res.json["message"] == "Order not found"


class TestOrderListAndCreation:
    def test_create_order_success(
        self,
        db: DBConfig,
        client: FlaskClient,
        regular_user: User,
        simple_customer: Customer,
        simple_book: Book,
        regular_user_headers: Mapping[str, str],
    ):

        original_qty = simple_book.qty

        data = dict(
            customer=str(simple_customer.id),
            due_date="2022-10-10",
            borrowed_books=[
                dict(
                    book_id=str(simple_book.id),
                    qty=4
                )
            ]
        )

        res = client.post("/api/v1/orders", json=data, headers=regular_user_headers)

        assert res.status_code == 201
        assert res.json["message"] == "order created"
        assert res.json["order"]["created_by"] == str(regular_user.id)
        assert res.json["order"]["borrowed_books"][0]["book_id"] == str(simple_book.id)

        updated_qty_check = Book.get(simple_book.id).qty

        assert original_qty != updated_qty_check
        assert updated_qty_check == (original_qty - 4)

    def test_create_order_success_2_books(
        self,
        db: DBConfig,
        client: FlaskClient,
        regular_user: User,
        simple_customer: Customer,
        simple_book: Book,
        simple_book_2: Book,
        regular_user_headers: Mapping[str, str],
    ):

        original_qty_1 = simple_book.qty
        original_qty_2 = simple_book_2.qty

        data = dict(
            customer=str(simple_customer.id),
            due_date="2022-10-10",
            borrowed_books=[
                dict(
                    book_id=str(simple_book.id),
                    qty=4
                ),
                dict(
                    book_id=str(simple_book_2.id),
                    qty=4
                ),
            ]
        )

        res = client.post("/api/v1/orders", json=data, headers=regular_user_headers)

        assert res.status_code == 201
        assert res.json["message"] == "order created"
        assert res.json["order"]["created_by"] == str(regular_user.id)
        assert res.json["order"]["borrowed_books"][0]["book_id"] == str(simple_book.id)

        updated_qty_check_1 = Book.get(simple_book.id).qty
        updated_qty_check_2 = Book.get(simple_book.id).qty

        assert original_qty_1 != updated_qty_check_1
        assert updated_qty_check_1 == (original_qty_1 - 4)

        assert original_qty_2 != updated_qty_check_2
        assert updated_qty_check_2 == (original_qty_2 - 4)

    def test_create_order_error_book_quantity_exceeded(
        self,
        db: DBConfig,
        client: FlaskClient,
        regular_user: User,
        simple_customer: Customer,
        simple_book: Book,
        regular_user_headers: Mapping[str, str],
    ):

        data = dict(
            customer=str(simple_customer.id),
            due_date="2022-10-10",
            borrowed_books=[
                dict(
                    book_id=str(simple_book.id),
                    qty=100
                )
            ]
        )

        res = client.post("/api/v1/orders", json=data, headers=regular_user_headers)

        assert res.status_code == 422
        assert res.json["borrowed_books"]["book"][0] == f"Quantity for this book {simple_book.id} is too much"

    def test_create_order_error_no_books(
        self,
        db: DBConfig,
        client: FlaskClient,
        regular_user: User,
        simple_customer: Customer,
        simple_book: Book,
        regular_user_headers: Mapping[str, str],
    ) -> None:

        data = dict(
            customer=str(simple_customer.id),
            due_date="2022-10-10",
            borrowed_books=[]
        )

        res = client.post("/api/v1/orders", json=data, headers=regular_user_headers)

        assert res.status_code == 422
        assert res.json["borrowed_books"][0] == "Borrowed book value cannot be empty."

    def test_get_orders_success(
        self,
        db: DBConfig,
        client: FlaskClient,
        simple_order: Customer,
        regular_user_headers: Mapping[str, str],
    ) -> None:

        res = client.get("/api/v1/orders", headers=regular_user_headers)

        assert res.status_code == 200
        assert len(res.json["orders"]) == 1
