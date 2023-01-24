import click
from flask.cli import with_appcontext

from shadow_lib.models import User, Author, Book, Customer, Order, BorrowedBook


@click.command("populate-db")
@with_appcontext
def populate_db() -> User:  # pragma: no cover
    superadmin = User(
        email="test@test.com", password="admin", is_active=True, role="superadmin"
    )
    superadmin.save()
    click.echo(f"Created superadmin user with email {superadmin.email}\n")

    customer = Customer(
        fullname="test customer",
        document_type="generic_id",
        document_id="1223123123",
        created_by_id=superadmin.id,
    )
    customer.save()
    click.echo(f"Created customer with id {customer.id}\n")

    author = Author(
        first_name="Author",
        last_name="Test",
        birth_date="1970-10-10",
        created_by_id=superadmin.id,
    )
    author.save()
    click.echo(f"Created author with id {author.id}\n")

    book = Book(
        title="Test book",
        EAN="1231-12312",
        SKU="23123123",
        release_date="1990-10-10",
        qty=20,
        created_by_id=superadmin.id,
    )

    book.authors.append(author)
    book.save()
    click.echo(f"Created book with id {book.id} and author with id {author.id}\n")

    order = Order(
        customer_id=customer.id,
        due_date="2022-10-10",
    )

    bb = BorrowedBook(
        book_id=book.id,
        qty=4,
    )

    order.borrowed_books.append(bb)
    order.save()

    click.echo(f"Created order with id {order.id} for book with id {book.id}\n")

    # Update book quantity
    book.qty -= 4
    book.save()
