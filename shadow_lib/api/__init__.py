from flask import Blueprint
from flask_restful import Api

from .resources import (
    Login,
    RefreshToken,
    RevokeAccessToken,
    RevokeRefreshToken,
    SwaggerJsonView,
    SwaggerView,
    UserChangePasswordResource,
    UserDetailResource,
    UserGetMeResource,
    UserListResource,
    UserRequestPasswordReset,
    AuthorDetailResource,
    AuthorListResource,
    BookDetailResource,
    BookListResource,
    CustomerDetailResource,
    CustomerListResource,
    OrderDetailResource,
    OrderListResource,
    BorrowedBookDetailResource,
    BorrowedBookListResource,
)

api_blueprint = Blueprint("api", __name__, url_prefix="/api/v1")

api = Api(api_blueprint)

# Swagger API
api.add_resource(SwaggerView, "/docs", methods=["GET"])
api.add_resource(
    SwaggerJsonView, "/docs/json", methods=["GET"], endpoint="api_swagger_json"
)

# Author apis
api.add_resource(
    AuthorDetailResource,
    "/authors/<uuid:author_id>",
    methods=["GET", "PATCH", "DELETE"],
)
api.add_resource(AuthorListResource, "/authors", methods=["GET", "POST"])

# Book apis
api.add_resource(
    BookDetailResource, "/books/<uuid:book_id>", methods=["GET", "PATCH", "DELETE"]
)
api.add_resource(BookListResource, "/books", methods=["GET", "POST"])

# Customer apis
api.add_resource(
    CustomerDetailResource,
    "/customers/<uuid:customer_id>",
    methods=["GET", "PATCH", "DELETE"],
)
api.add_resource(CustomerListResource, "/customers", methods=["GET", "POST"])

# Order apis
api.add_resource(
    OrderDetailResource,
    "/orders/<uuid:order_id>",
    methods=["GET", "PATCH", "DELETE"],
)
api.add_resource(OrderListResource, "/orders", methods=["GET", "POST"])

# BorrowedBook apis
api.add_resource(
    BorrowedBookDetailResource,
    "/borrowed-books/<uuid:borrowed_book_id>",
    methods=["GET", "PATCH", "DELETE"],
)
api.add_resource(BorrowedBookListResource, "/borrowed-books", methods=["GET", "POST"])

# User apis
api.add_resource(
    UserDetailResource, "/users/<uuid:user_id>", methods=["GET", "PATCH", "DELETE"]
)
api.add_resource(UserListResource, "/users", methods=["GET", "POST"])
api.add_resource(UserGetMeResource, "/users/me", methods=["GET"])

# Password apis
api.add_resource(UserChangePasswordResource, "/users/change-password")
api.add_resource(UserRequestPasswordReset, "/users/reset-password", methods=["POST"])
api.add_resource(
    UserRequestPasswordReset,
    "/users/reset-password/",
    methods=["POST"],
    endpoint="dead_endpoint",
)
api.add_resource(
    UserRequestPasswordReset,
    "/users/reset-password/<string:token>",
    methods=["PATCH", "GET"],
    endpoint="do_reset",
)

# Token management apis
api.add_resource(RefreshToken, "/refresh-token")
api.add_resource(RevokeAccessToken, "/revoke-access-token")
api.add_resource(RevokeRefreshToken, "/revoke-refresh-token")

# Auth apis
api.add_resource(Login, "/login")
