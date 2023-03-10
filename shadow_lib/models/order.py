import uuid

from typing import Any

from flask import abort

from sqlalchemy import Column, Date, Integer, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql.expression import false

from sqlalchemy.orm import relationship
from sqlalchemy.sql import select

from .db import db
from .model_errors import (
    ORDER_NOT_FOUND_ERR_MESSAGE,
    BORROWED_BOOK_NOT_FOUND_ERR_MESSAGE,
)


class BorrowedBook(db.Model):  # type: ignore
    __tablename__ = "borrowed_books"

    id = Column(
        UUID(as_uuid=True), default=uuid.uuid4, nullable=False, primary_key=True
    )

    order_id = Column(
        UUID(as_uuid=True),
        ForeignKey("orders.id"),
        nullable=False,
    )

    book_id = Column(
        UUID(as_uuid=True),
        ForeignKey("books.id"),
        nullable=False,
    )

    order = relationship("Order", back_populates="borrowed_books")
    book = relationship("Book", back_populates="borrowed_books")

    qty = Column(Integer, nullable=False, default=0)

    @staticmethod
    def get_borrowed_book(borrowed_book_id: uuid.UUID, current_user: Any) -> "Order":
        br_book_query = select(BorrowedBook).where(BorrowedBook.id == borrowed_book_id)
        br_book = db.session.execute(br_book_query).unique().scalar_one_or_none()

        if not br_book:
            return abort(404, BORROWED_BOOK_NOT_FOUND_ERR_MESSAGE)

        return br_book

    @staticmethod
    def get_borrowed_books(current_user: Any) -> list["Order"]:
        br_book_query = select(BorrowedBook)
        br_books = db.session.execute(br_book_query).unique().scalars().all()
        return br_books


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

    has_been_returned = Column(Boolean, nullable=False, default=False)
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
        order_query = select(Order).where(
            Order.id == order_id, Order.has_been_returned == false()
        )
        order = db.session.execute(order_query).unique().scalar_one_or_none()

        if not order:
            return abort(404, ORDER_NOT_FOUND_ERR_MESSAGE)

        return order

    @staticmethod
    def get_orders(current_user: Any) -> list["Order"]:
        order_query = select(Order)
        orders = db.session.execute(order_query).unique().scalars().all()
        return orders
