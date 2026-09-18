import httpx

from auth.api_key import ApiKeyAuth
from auth.base import AuthError
from auth.session_auth import SessionAuth


def test_api_key_auth_sets_bearer_and_x_token_headers_without_logging_value():
    client = httpx.Client(base_url="https://crawler.test")
    provider = ApiKeyAuth("secret-api-key")

    provider.authenticate(client)

    assert client.headers["Authorization"] == "Bearer secret-api-key"
    assert client.headers["x-token"] == "secret-api-key"
    assert "secret-api-key" not in repr(provider)


def test_session_auth_posts_observed_login_payload_and_sets_token_headers():
    requests = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(
            200,
            json={
                "data": {
                    "user_id": "u-1",
                    "token": "access-token",
                    "refresh_token": "refresh-token",
                    "token_type": "Bearer",
                },
                "status": "success",
            },
            request=request,
        )

    client = httpx.Client(transport=httpx.MockTransport(handler), base_url="https://crawler.test")
    SessionAuth("qa@example.test", "secret-password").authenticate(client)

    assert requests[0].url.path == "/api-non/v1.0/users/login"
    assert requests[0].content == b'{"email":"qa@example.test","password":"secret-password"}'
    assert client.headers["Authorization"] == "Bearer access-token"
    assert client.headers["x-token"] == "access-token"


def test_session_auth_reports_safe_failure_reason():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(401, json={"detail": "Invalid credentials"}, request=request)

    client = httpx.Client(transport=httpx.MockTransport(handler), base_url="https://crawler.test")

    try:
        SessionAuth("qa@example.test", "secret-password").authenticate(client)
    except AuthError as exc:
        assert "Invalid credentials" in str(exc)
        assert "secret-password" not in str(exc)
    else:
        raise AssertionError("AuthError was not raised")
