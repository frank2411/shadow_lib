import uuid

from typing import Any
from flask import abort

from sqlalchemy import Column, Date, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID

from sqlalchemy.orm import relationship
from sqlalchemy.sql import select
from .model_errors import AUTHOR_NOT_FOUND_ERR_MESSAGE

from .db import db


class BookAuthor(db.Model):  # type: ignore
    __tablename__ = "book_authors"

    author_id = Column(
        UUID(as_uuid=True), ForeignKey("authors.id"), nullable=False, primary_key=True
    )
    book_id = Column(
        UUID(as_uuid=True), ForeignKey("books.id"), nullable=False, primary_key=True
    )


class Author(db.Model):  # type: ignore
    __tablename__ = "authors"

    id = Column(
        UUID(as_uuid=True), default=uuid.uuid4, nullable=False, primary_key=True
    )

    first_name = Column(String(255), nullable=False)
    last_name = Column(String(255), nullable=False)
    birth_date = Column(Date)

    created_by_id = Column(
        UUID(as_uuid=True), ForeignKey("backoffice_users.id", ondelete="SET NULL")
    )

    books = relationship(
        "Book",
        secondary="book_authors",
        back_populates="authors",
        lazy="select",
    )

    @staticmethod
    def get_author(author_id: uuid.UUID, current_user: Any) -> "Author":
        author_query = select(Author).where(Author.id == author_id)
        author = db.session.execute(author_query).unique().scalar_one_or_none()

        if not author:
            return abort(404, AUTHOR_NOT_FOUND_ERR_MESSAGE)

        return author

    @staticmethod
    def get_authors(current_user: Any) -> list["Author"]:
        author_query = select(Author)
        authors = db.session.execute(author_query).unique().scalars().all()
        return authors
