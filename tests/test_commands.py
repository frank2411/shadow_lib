from click.testing import CliRunner
from flask.testing import FlaskClient

from shadow_lib.commands import create_superadmin, create_superadmin_token
from shadow_lib.models import User
from shadow_lib.models.db import DBConfig


class TestSuperadmin:
    def test_creation_success(self, db: DBConfig, client: FlaskClient, superadmin: User) -> None:
        runner = CliRunner()

        email = "superuser2@email.com"
        password = "test2"

        result = runner.invoke(create_superadmin, ["--email", email, "--password", password])
        assert result.exit_code == 0
        assert f"Created superadmin user with email {email}" in result.output


class TestSuperadminToken:
    def test_token_creation_success(self, db: DBConfig, client: FlaskClient, superadmin: User) -> None:
        runner = CliRunner()

        result = runner.invoke(create_superadmin_token, ["--email", superadmin.email, "--password", "test"])
        assert result.exit_code == 0
        assert f"Created token for superadmin user with email {superadmin.email}" in result.output

    def test_token_creation_pwd_fail(self, db: DBConfig, client: FlaskClient, superadmin: User) -> None:
        runner = CliRunner()
        result = runner.invoke(create_superadmin_token, ["--email", superadmin.email, "--password", "pwd"])

        assert result.exit_code == 2
        assert "Password is not correct" in result.output

    def test_token_creation_no_user(self, db: DBConfig, client: FlaskClient) -> None:
        runner = CliRunner()
        result = runner.invoke(create_superadmin_token, ["--email", "test", "--password", "pwd"])

        assert result.exit_code == 2
        assert "This user does not exist. Please contact the administrators." in result.output
