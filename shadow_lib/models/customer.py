import uuid
import enum

from flask import abort

from typing import Any

from sqlalchemy import Column, Enum, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID

from sqlalchemy.orm import relationship
from sqlalchemy.sql import select

from .db import db

from .model_errors import CUSTOMER_NOT_FOUND_ERR_MESSAGE


class CustomerDocumentTypes(str, enum.Enum):
    generic_id = "generic_id"
    passport = "passport"
    driver_license = "driver_license"


class Customer(db.Model):  # type: ignore
    __tablename__ = "customers"

    id = Column(
        UUID(as_uuid=True), default=uuid.uuid4, nullable=False, primary_key=True
    )

    fullname = Column(String(255), nullable=False)
    document_type = Column(
        Enum(CustomerDocumentTypes), nullable=False, default="generic_id"
    )
    document_id = Column(String(255), nullable=False)

    created_by_id = Column(
        UUID(as_uuid=True), ForeignKey("backoffice_users.id", ondelete="SET NULL")
    )

    orders = relationship(
        "Order",
        backref="customer",
        lazy="joined",
        cascade="all,delete-orphan",
        passive_deletes=True,
    )

    @staticmethod
    def get_customer(customer_id: uuid.UUID, current_user: Any) -> "Customer":
        customer_query = select(Customer).where(Customer.id == customer_id)
        customer = db.session.execute(customer_query).unique().scalar_one_or_none()

        if not customer:
            return abort(404, CUSTOMER_NOT_FOUND_ERR_MESSAGE)

        return customer

    @staticmethod
    def get_customers(current_user: Any) -> list["Customer"]:
        customer_query = select(Customer)
        customers = db.session.execute(customer_query).unique().scalars().all()
        return customers
