from datetime import timedelta
from typing import Optional

import click
from flask.cli import with_appcontext

from shadow_lib.jwt import JwtTokenManager
from shadow_lib.models import Token, User


@click.command("create-superadmin")
@click.option("--email", "email", required=True, type=click.STRING)
@click.option("--password", "password", required=True, type=click.STRING)
@with_appcontext
def create_superadmin(email: str, password: str) -> User:
    superadmin = User(email=email, password=password, is_active=True, role="superadmin")
    superadmin.save()
    click.echo(f"Created superadmin user with email {superadmin.email}\n\n")
    return superadmin


@click.command("create-superadmin-token")
@click.option("--email", "email", required=True, type=click.STRING)
@click.option("--password", "password", required=True, type=click.STRING)
@with_appcontext
def create_superadmin_token(email: str, password: str) -> User:
    superadmin: Optional[User] = User.query.filter_by(
        email=email, is_active=True, role="superadmin"
    ).one_or_none()
    if not superadmin:
        raise click.UsageError(
            "This user does not exist. Please contact the administrators."
        )
    if not superadmin.check_password(password):
        raise click.UsageError("Password is not correct.")

    # 2 years expiration
    access_token_expiration_delta = timedelta(days=(365 * 2))
    # 3 years expiration
    refresh_token_expiration_delta = timedelta(days=(365 * 3))

    access_token_encoded, refresh_token_encoded = Token.create_tokens(
        superadmin, access_token_expiration_delta, refresh_token_expiration_delta
    )

    access_token = JwtTokenManager.decode_token(access_token_encoded, "access")
    refresh_token = JwtTokenManager.decode_token(refresh_token_encoded, "refresh")

    click.echo(f"Created token for superadmin user with email {superadmin.email}\n")
    click.echo(f"Access token id: {access_token['jti']}\n")
    click.echo(f"Refresh token id: {refresh_token['jti']}\n\n")
    click.echo(f"Access token: {access_token_encoded}\n")
    click.echo(f"Refresh token: {refresh_token_encoded}\n\n")

    return superadmin
