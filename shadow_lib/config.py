import os

from dotenv import load_dotenv

load_dotenv()


class BaseConfig:
    SECRET_KEY = os.getenv("SECRET_KEY", "localkey")
    ENV = os.getenv("ENV", "local")

    FRONTEND_URL = "myfrontend"
    # Token expiration time in minutes
    ACCESS_TOKEN_DELTA: int = int(os.getenv("ACCESS_TOKEN_DELTA", 5))
    REFRESH_TOKEN_DELTA: int = int(os.getenv("REFRESH_TOKEN_DELTA", 2))


class ProductionConfig(BaseConfig):
    DEBUG = False
    TESTING = False

    SHADOW_LIB_DB_ENGINE = os.getenv("SHADOW_LIB_DB_ENGINE")
    SHADOW_LIB_DB_USER = os.getenv("SHADOW_LIB_DB_USER")
    SHADOW_LIB_DB_PASSWORD = os.getenv("SHADOW_LIB_DB_PASSWORD")
    SHADOW_LIB_DB_HOST = os.getenv("SHADOW_LIB_DB_HOST")
    SHADOW_LIB_DB_PORT = os.getenv("SHADOW_LIB_DB_PORT")
    SHADOW_LIB_DB_NAME = os.getenv("SHADOW_LIB_DB_NAME")

    SQLALCHEMY_DATABASE_URI = (
        f"{SHADOW_LIB_DB_ENGINE}://{SHADOW_LIB_DB_USER}:"
        f"{SHADOW_LIB_DB_PASSWORD}@{SHADOW_LIB_DB_HOST}:"
        f"{SHADOW_LIB_DB_PORT}/{SHADOW_LIB_DB_NAME}"
    )


class DevelopConfig(BaseConfig):
    DEBUG = True
    TESTING = False

    SHADOW_LIB_DB_ENGINE = os.getenv("SHADOW_LIB_DB_ENGINE")
    SHADOW_LIB_DB_USER = os.getenv("SHADOW_LIB_DB_USER")
    SHADOW_LIB_DB_PASSWORD = os.getenv("SHADOW_LIB_DB_PASSWORD")
    SHADOW_LIB_DB_HOST = os.getenv("SHADOW_LIB_DB_HOST")
    SHADOW_LIB_DB_PORT = os.getenv("SHADOW_LIB_DB_PORT")
    SHADOW_LIB_DB_NAME = os.getenv("SHADOW_LIB_DB_NAME")

    SQLALCHEMY_DATABASE_URI = (
        f"{SHADOW_LIB_DB_ENGINE}://{SHADOW_LIB_DB_USER}:"
        f"{SHADOW_LIB_DB_PASSWORD}@{SHADOW_LIB_DB_HOST}:"
        f"{SHADOW_LIB_DB_PORT}/{SHADOW_LIB_DB_NAME}"
    )


class LocalConfig(BaseConfig):
    DEBUG = True
    TESTING = False

    SHADOW_LIB_DB_ENGINE = os.getenv("SHADOW_LIB_DB_ENGINE", "postgresql")
    SHADOW_LIB_DB_USER = os.getenv("SHADOW_LIB_DB_USER", "postgres")
    SHADOW_LIB_DB_PASSWORD = os.getenv("SHADOW_LIB_DB_PASSWORD", "admin")
    SHADOW_LIB_DB_HOST = os.getenv("SHADOW_LIB_DB_HOST", "localhost")
    SHADOW_LIB_DB_PORT = os.getenv("SHADOW_LIB_DB_PORT", "5432")
    SHADOW_LIB_DB_NAME = os.getenv("SHADOW_LIB_DB_NAME", "shadow_lib")

    SQLALCHEMY_DATABASE_URI = (
        f"{SHADOW_LIB_DB_ENGINE}://{SHADOW_LIB_DB_USER}:"
        f"{SHADOW_LIB_DB_PASSWORD}@{SHADOW_LIB_DB_HOST}:"
        f"{SHADOW_LIB_DB_PORT}/{SHADOW_LIB_DB_NAME}"
    )

    EMAIL_SENDER_ADDRESS = "noreply@test.com"
    EMAIL_HOST = "localhost"
    EMAIL_PORT = 1025
    EMAIL_USE_TLS = False


class TestConfig(BaseConfig):
    DEBUG = False
    TESTING = True

    SHADOW_LIB_DB_ENGINE = os.getenv("TEST_DB_ENGINE", "postgresql")
    SHADOW_LIB_DB_USER = os.getenv("TEST_DB_USER", "postgres")
    SHADOW_LIB_DB_PASSWORD = os.getenv("TEST_DB_PASSWORD", "admin")
    SHADOW_LIB_DB_HOST = os.getenv("TEST_DB_HOST", "localhost")
    SHADOW_LIB_DB_PORT = os.getenv("TEST_DB_PORT", "5432")
    SHADOW_LIB_DB_NAME = os.getenv("TEST_DB_NAME", "test_db")

    SQLALCHEMY_DATABASE_URI = (
        f"{SHADOW_LIB_DB_ENGINE}://{SHADOW_LIB_DB_USER}:"
        f"{SHADOW_LIB_DB_PASSWORD}@{SHADOW_LIB_DB_HOST}:"
        f"{SHADOW_LIB_DB_PORT}/{SHADOW_LIB_DB_NAME}"
    )

    EMAIL_SENDER_ADDRESS = "noreply@edf-sf.com"
    EMAIL_HOST = "localhost"
    EMAIL_PORT = 1025
    EMAIL_USE_TLS = False
