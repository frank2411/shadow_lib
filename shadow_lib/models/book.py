import uuid

from typing import Any
from flask import abort

from sqlalchemy import Column, Date, Integer, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID

from sqlalchemy.orm import relationship
from sqlalchemy.sql import select

from shadow_lib.models import Author, BookAuthor
from .model_errors import BOOK_NOT_FOUND_ERR_MESSAGE
from sqlalchemy import or_

from .db import db


class Book(db.Model):  # type: ignore
    __tablename__ = "books"

    id = Column(
        UUID(as_uuid=True), default=uuid.uuid4, nullable=False, primary_key=True
    )

    title = Column(String(255), nullable=False)
    EAN = Column(String(255), nullable=False)
    SKU = Column(String(255), nullable=False)

    release_date = Column(Date, nullable=False)

    qty = Column(Integer, nullable=False, default=0)
    created_by_id = Column(
        UUID(as_uuid=True), ForeignKey("backoffice_users.id", ondelete="SET NULL")
    )

    borrowed_books = relationship(
        "BorrowedBook",
        back_populates="book",
        lazy="select",
        cascade="all, delete-orphan",
    )

    authors = relationship(
        "Author",
        secondary="book_authors",
        back_populates="books",
        lazy="joined",
    )

    @staticmethod
    def get_book(book_id: uuid.UUID, current_user: Any) -> "Book":
        book_query = select(Book).where(Book.id == book_id)
        book = db.session.execute(book_query).unique().scalar_one_or_none()

        if not book:
            return abort(404, BOOK_NOT_FOUND_ERR_MESSAGE)

        return book

    @staticmethod
    def get_books(current_user: Any) -> list["Book"]:
        book_query = select(Book)
        books = db.session.execute(book_query).unique().scalars().all()
        return books

    @staticmethod
    def search_books(current_user: Any, valid_filters: dict = None) -> list["Book"]:
        book_query = select(Book).join(BookAuthor).join(Author)
        book_query = book_query.where(
            or_(
                Book.title.ilike("%" + valid_filters["q"] + "%"),
                Author.first_name.ilike("%" + valid_filters["q"] + "%"),
                Author.last_name.ilike("%" + valid_filters["q"] + "%"),
                Book.EAN.ilike("%" + valid_filters["q"] + "%"),
                Book.SKU.ilike("%" + valid_filters["q"] + "%"),
            )
        )

        # if valid_filters.get("release_date"):
        #     book_query = book_query.where(
        #         Book.release_date == valid_filters["release_date"]
        #     )

        books = db.session.execute(book_query).unique().scalars().all()
        return books

        # courses = courses.filter(models.Course.name.like('%' + searchForm.courseName.data + '%'))
