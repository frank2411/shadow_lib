import uuid
from typing import Mapping

from flask.testing import FlaskClient

from shadow_lib.models import CUSTOMER_NOT_FOUND_ERR_MESSAGE, Customer, User
from shadow_lib.models.db import DBConfig


class TestCustomerDetailRetrieve:
    def test_get_book_success(
        self,
        db: DBConfig,
        client: FlaskClient,
        simple_customer: Customer,
        regular_user_headers: Mapping[str, str],
    ) -> None:

        res = client.get(f"/api/v1/customers/{simple_customer.id}", headers=regular_user_headers)

        assert res.status_code == 200
        assert res.json
        assert res.json["customer"]["id"] == str(simple_customer.id)
        assert res.json["customer"]["orders"] == []

    def test_get_book_not_found(
        self,
        db: DBConfig,
        client: FlaskClient,
        random_uuid: uuid.UUID,
        regular_user_headers: Mapping[str, str],
    ) -> None:

        res = client.get(f"/api/v1/customers/{random_uuid}", headers=regular_user_headers)

        assert res.status_code == 404
        assert res.json
        assert res.json["message"] == CUSTOMER_NOT_FOUND_ERR_MESSAGE


class TestCustomerDetailGetAndUpdateAndDelete:

    def test_update_customer(
        self,
        db: DBConfig,
        client: FlaskClient,
        simple_customer: Customer,
        regular_user_headers: Mapping[str, str],
    ) -> None:

        data = {
            "fullname": "another test"
        }

        res = client.patch(f"/api/v1/customers/{simple_customer.id}", json=data, headers=regular_user_headers)

        assert res.status_code == 200
        assert res.json
        assert res.json["customer"]["id"] == str(simple_customer.id)
        assert res.json["customer"]["fullname"] == data["fullname"]

    def test_update_customer_fail_unkown_field(
        self,
        db: DBConfig,
        client: FlaskClient,
        simple_customer: Customer,
        regular_user_headers: Mapping[str, str],
    ) -> None:

        data = {
            "orders": ["wetry"]
        }

        res = client.patch(f"/api/v1/customers/{simple_customer.id}", json=data, headers=regular_user_headers)

        assert res.status_code == 422
        assert res.json
        assert res.json["orders"][0] == "Unknown field."

    def test_delete_customer_success(
        self,
        db: DBConfig,
        client: FlaskClient,
        simple_customer: Customer,
        regular_user_headers: Mapping[str, str],
    ) -> None:

        res = client.delete(f"/api/v1/customers/{simple_customer.id}", headers=regular_user_headers)

        assert res.status_code == 200
        assert res.json["message"] == "customer deleted"

    def test_delete_customer_fail_customer_not_found(
        self,
        db: DBConfig,
        client: FlaskClient,
        random_uuid: uuid.UUID,
        regular_user_headers: Mapping[str, str],
    ) -> None:

        res = client.delete(f"/api/v1/customers/{random_uuid}", headers=regular_user_headers)

        assert res.status_code == 404
        assert res.json["message"] == "Customer not found"


class TestCustomerListAndCreation:
    def test_create_customer_success(
        self,
        db: DBConfig,
        client: FlaskClient,
        regular_user: User,
        regular_user_headers: Mapping[str, str],
    ):

        data = dict(
            fullname="customer test 324",
            document_type="generic_id",
            document_id="1231231231223",
        )

        res = client.post("/api/v1/customers", json=data, headers=regular_user_headers)

        assert res.status_code == 201
        assert res.json["message"] == "customer created"
        assert res.json["customer"]["created_by"] == str(regular_user.id)

    def test_create_customer_error_empty_document_id(
        self,
        db: DBConfig,
        client: FlaskClient,
        regular_user_headers: Mapping[str, str],
    ):

        data = dict(
            fullname="customer test",
            document_type="generic_id",
        )

        res = client.post("/api/v1/customers", json=data, headers=regular_user_headers)

        assert res.status_code == 422
        assert res.json["document_id"][0] == "Missing data for required field."

    def test_get_customers_success(
        self,
        db: DBConfig,
        client: FlaskClient,
        simple_customer: Customer,
        superadmin_headers: Mapping[str, str],
    ) -> None:

        res = client.get("/api/v1/customers", headers=superadmin_headers)

        assert res.status_code == 200
        assert len(res.json["customers"]) == 1
