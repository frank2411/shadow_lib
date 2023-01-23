from unittest.mock import Mock, patch

import pytest
from shadow_lib.decorators import authenticate_user, check_bearer_token


class SideEffectException(Exception):
    def __init__(self, message, *args, **kwargs):
        self.message = message


class TestAuthorizationDecorators:

    @patch('shadow_lib.decorators.request', spec={})
    @patch('shadow_lib.decorators.abort')
    def test_auth_decorator_success(self, abort_mock, request_mock, generic_headers):
        fn = Mock()
        fn.return_value = "returned"

        request_mock.headers = generic_headers

        dec = check_bearer_token(fn)
        ret = dec()

        assert ret == "returned"

    @patch('shadow_lib.decorators.request', spec={})
    @patch('shadow_lib.decorators.abort')
    def test_auth_decorator_malformed_auth_header_no_bearer(self, abort_mock, request_mock):
        headers = {
            "content-type": "application/json",
            "authorization": "123123123123",
        }

        fn = Mock()
        fn.return_value = "returned"
        abort_mock.side_effect = SideEffectException("No Bearer")

        request_mock.headers = headers

        with pytest.raises(SideEffectException) as httperror:
            dec = check_bearer_token(fn)
            dec()

        assert httperror.value
        assert httperror.value.message == "No Bearer"

    @patch('shadow_lib.decorators.request', spec={})
    @patch('shadow_lib.decorators.abort')
    def test_auth_decorator_malformed_auth_header_no_token(self, abort_mock, request_mock):
        headers = {
            "content-type": "application/json",
            "authorization": "Bearer",
        }

        fn = Mock()
        fn.return_value = "returned"
        abort_mock.side_effect = SideEffectException("No Token")

        request_mock.headers = headers

        with pytest.raises(SideEffectException) as httperror:
            dec = check_bearer_token(fn)
            dec()

        assert httperror.value
        assert httperror.value.message == "No Token"

    @patch('shadow_lib.decorators.request', spec={})
    @patch('shadow_lib.decorators.abort')
    def test_auth_decorator_malformed_auth_header_uncorrect_bearer(self, abort_mock, request_mock):
        headers = {
            "content-type": "application/json",
            "authorization": "Bear 123123123123",
        }

        fn = Mock()
        fn.return_value = "returned"
        abort_mock.side_effect = SideEffectException("Malformed Bearer")

        request_mock.headers = headers

        with pytest.raises(SideEffectException) as httperror:
            dec = check_bearer_token(fn)
            dec()

        assert httperror.value
        assert httperror.value.message == "Malformed Bearer"

    @patch('shadow_lib.decorators.request', spec={})
    @patch('shadow_lib.decorators.abort')
    def test_auth_decorator_no_auth_header(self, abort_mock, request_mock):
        headers = {
            "content-type": "application/json",
        }

        fn = Mock()
        fn.return_value = "returned"
        abort_mock.side_effect = SideEffectException("No auth header")

        request_mock.headers = headers

        with pytest.raises(SideEffectException) as httperror:
            dec = check_bearer_token(fn)
            dec()

        assert httperror.value
        assert httperror.value.message == "No auth header"


class TestAuthenticateDecorator:

    @patch('shadow_lib.decorators.request', spec={})
    @patch('shadow_lib.decorators.abort')
    def test_authenticate_user_valid(self, abort_mock, request_mock, generic_headers, access_token):
        headers = {
            "content-type": "application/json",
            "authorization": f"Bearer {access_token}",
        }

        fn = Mock()
        fn.return_value = "returned"
        request_mock.headers = headers

        dec = authenticate_user(fn)
        ret = dec()

        assert ret == "returned"

    @patch('shadow_lib.decorators.request', spec={})
    @patch('shadow_lib.decorators.Token.set_current_user')
    def test_authenticate_user_aborted(self, token_mock, request_mock, generic_headers, access_token):
        headers = {
            "content-type": "application/json",
            "authorization": f"Bearer {access_token}",
        }

        fn = Mock()
        fn.return_value = "returned"
        request_mock.headers = headers
        token_mock.side_effect = SideEffectException("Something went wrong")

        with pytest.raises(SideEffectException) as httperror:
            dec = authenticate_user(fn)
            dec()

        assert httperror.value
        assert httperror.value.message == "Something went wrong"
