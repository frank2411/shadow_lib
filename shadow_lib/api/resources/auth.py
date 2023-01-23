from flask import current_app, request
from flask_restful import Resource

from shadow_lib.custom_types import SuccessResponseType
from shadow_lib.models import Token, User


class Login(Resource):
    def post(self) -> SuccessResponseType:
        if not request.is_json:
            return {"message": "Missing JSON in request"}, 400

        if not request.json:
            return {"message": "Missing credentials"}, 400

        email = request.json.get("email", None)
        password = request.json.get("password", None)

        if not email or not password:
            return {"message": "Missing credentials"}, 400

        user = User.get_user_for_login(email, password)
        access_token, refresh_token = Token.create_tokens(user)

        ret = {
            "access_token": access_token,
            "refresh_token": refresh_token,
        }
        current_app.logger.info(f"Token has been created for user {user.id}")
        return ret, 200
