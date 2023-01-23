import uuid

from typing import Any

from flask import abort

from sqlalchemy import Column, Date, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID

from sqlalchemy.orm import relationship
from sqlalchemy.sql import select

from .db import db
from .model_errors import ORDER_NOT_FOUND_ERR_MESSAGE


class BorrowedBook(db.Model):  # type: ignore
    __tablename__ = "borrowed_books"

    order_id = Column(
        UUID(as_uuid=True),
        ForeignKey("orders.id"),
        nullable=False,
        primary_key=True,
    )
    book_id = Column(
        UUID(as_uuid=True),
        ForeignKey("books.id"),
        nullable=False,
        primary_key=True,
    )
    order = relationship("Order", back_populates="borrowed_books")
    book = relationship("Book", back_populates="borrowed_books")

    qty = Column(Integer, nullable=False, default=0)


class Order(db.Model):  # type: ignore
    __tablename__ = "orders"

    id = Column(
        UUID(as_uuid=True), default=uuid.uuid4, nullable=False, primary_key=True
    )

    customer_id = Column(
        UUID(as_uuid=True),
        ForeignKey("customers.id", ondelete="CASCADE"),
        nullable=False,
    )

    due_date = Column(Date, nullable=False)

    created_by_id = Column(
        UUID(as_uuid=True), ForeignKey("backoffice_users.id", ondelete="SET NULL")
    )

    borrowed_books = relationship(
        "BorrowedBook",
        back_populates="order",
        lazy="joined",
        cascade="all, delete-orphan",
    )

    @staticmethod
    def get_order(order_id: uuid.UUID, current_user: Any) -> "Order":
        order_query = select(Order).where(Order.id == order_id)
        order = db.session.execute(order_query).unique().scalar_one_or_none()

        if not order:
            return abort(404, ORDER_NOT_FOUND_ERR_MESSAGE)

        return order

    @staticmethod
    def get_orders(current_user: Any) -> list["Order"]:
        order_query = select(Order)
        orders = db.session.execute(order_query).unique().scalars().all()
        return orders
