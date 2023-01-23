from .auth import Login
from .swagger import SwaggerJsonView, SwaggerView
from .user import (
    UserChangePasswordResource,
    UserDetailResource,
    UserGetMeResource,
    UserListResource,
    UserRequestPasswordReset,
)
from .token import RefreshToken, RevokeAccessToken, RevokeRefreshToken
from .author import AuthorDetailResource, AuthorListResource
from .book import BookDetailResource, BookListResource
from .customer import CustomerDetailResource, CustomerListResource
from .order import OrderDetailResource, OrderListResource


__all__ = [
    "SwaggerView",
    "SwaggerJsonView",
    "UserDetailResource",
    "UserListResource",
    "UserGetMeResource",
    "UserChangePasswordResource",
    "UserRequestPasswordReset",
    "RefreshToken",
    "RevokeAccessToken",
    "RevokeRefreshToken",
    "Login",
    "AuthorDetailResource",
    "AuthorListResource",
    "BookDetailResource",
    "BookListResource",
    "CustomerDetailResource",
    "CustomerListResource",
    "OrderDetailResource",
    "OrderListResource",
]
