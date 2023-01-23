import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, Tuple

import jwt
from flask import abort, current_app


class JwtTokenManager:
    """Contains methods that can be used to encode and decode JWT tokens.
    See RFC 7519 for explanations about JWT: https://www.rfc-editor.org/rfc/rfc7519.html
    """

    TOKEN_TYPES = ["access", "refresh"]

    @classmethod
    def encode_token(
        cls,
        additional_token_data: Dict[str, Any],
        token_type: str,
        expiration_delta: timedelta,
        algorithm: str = "HS256",
    ) -> Tuple[str, Dict[str, Any]]:
        """Encode data to a JWT encoded format.

        Args:
            additional_token_data: token data to encode
            token_type: "access" or "refresh"
            expiration_delta: token expiration time.
            algorithm: JWT signing algorithm, "HS256" (default) or "RS256"

        Returns:
            Tuple with the encoded token string as the first item, and the raw token dict as the second item.
        """
        if token_type not in cls.TOKEN_TYPES:  # pragma: no cover
            raise ValueError(f"token_type must be one of {cls.TOKEN_TYPES}")

        uid = str(uuid.uuid4())
        now = datetime.utcnow()

        secret = current_app.config["SECRET_KEY"]

        token_data = {
            "iat": now,
            "nbf": now,
            "jti": uid,
            "type": token_type,
            "iss": "shadow_lib",
        }

        token_data["exp"] = now + expiration_delta

        token_data.update(additional_token_data)
        encoded_token: str = jwt.encode(token_data, secret, algorithm)

        return encoded_token, token_data

    @classmethod
    def decode_token(
        cls,
        token: str,
        token_type: str,
        algorithm: Tuple = ("HS256",),
        extra_required_claims: Tuple = (),
    ) -> Dict[str, object]:
        """Decode an encoded JWT.

        Args:
            token: encoded JWT
            token_type: "access" or "refresh"
            algorithm: JWT signing algorithms

        Returns:
            Token dict data.
        """
        required_claims = list(
            set(["jti", "exp", "type"] + list(extra_required_claims))
        )

        secret = current_app.config["SECRET_KEY"]

        try:
            payload: Dict[str, object] = jwt.decode(
                token, secret, list(algorithm), options={"require": required_claims}
            )
        except jwt.ExpiredSignatureError:
            abort(401, "Token has expired. Please login again")
        except jwt.InvalidTokenError:
            abort(401, "Token claims are missing or token is malformed")

        if payload["type"] != token_type:
            abort(401, "Wrong token type")

        return payload
