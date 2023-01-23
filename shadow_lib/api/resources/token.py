from flask import abort, current_app, request
from flask_restful import Resource

from shadow_lib.custom_types import SuccessResponseType
from shadow_lib.models import TOKEN_NOT_PROVIDED_ERR_MESSAGE, Token


class RefreshToken(Resource):
    def post(self) -> SuccessResponseType:
        if not request.is_json or request.json is None:
            return {"message": "Missing JSON in request"}, 400

        refresh_token = request.json.get("refresh_token", None)
        if not refresh_token:
            abort(403, TOKEN_NOT_PROVIDED_ERR_MESSAGE)

        access_token = Token.refresh_token(refresh_token)
        response = {
            "access_token": access_token,
        }
        current_app.logger.info("Token has been refreshed")
        return response, 200


class RevokeAccessToken(Resource):
    def post(self) -> SuccessResponseType:
        if not request.is_json or request.json is None:
            return {"message": "Missing JSON in request"}, 400

        access_token = request.json.get("access_token", None)

        if not access_token:
            abort(403, TOKEN_NOT_PROVIDED_ERR_MESSAGE)

        Token.revoke_token(access_token, token_type="access")
        current_app.logger.info("Token has been revoked")
        return {"message": "Token has been revoked"}


class RevokeRefreshToken(Resource):
    def post(self) -> SuccessResponseType:
        if not request.is_json or request.json is None:
            return {"message": "Missing JSON in request"}, 400

        refresh_token = request.json.get("refresh_token", None)

        if not refresh_token:
            abort(403, TOKEN_NOT_PROVIDED_ERR_MESSAGE)

        Token.revoke_token(refresh_token, token_type="refresh")
        current_app.logger.info("Token has been revoked")
        return {"message": "Token has been revoked"}
