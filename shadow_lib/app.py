import os

from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS

from .api import api_blueprint
from .models import db

# Example for commands imports
from .commands import create_superadmin, create_superadmin_token


load_dotenv()


def create_app(testing: bool = False) -> Flask:
    app = Flask("shadow_lib")

    config_path = os.getenv("SHADOW_LIB_CONFIG_PATH", "shadow_lib.config.LocalConfig")
    app.config.from_object(config_path)

    if testing is True:
        app.config["TESTING"] = True

    CORS(app)

    # Init db extension
    db.init_app(app)

    app.register_blueprint(api_blueprint)

    # Register general commands
    app.cli.add_command(create_superadmin)
    app.cli.add_command(create_superadmin_token)
    return app
