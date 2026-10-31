from datetime import timedelta

import pytest
from fastapi.testclient import TestClient

from app.core.security import create_access_token

LOGIN = "/api/v1/auth/login"
ME = "/api/v1/auth/me"


def test_login_returns_a_token_that_grants_access(
    client: TestClient, admin: tuple[str, str]
) -> None:
    username, password = admin

    login = client.post(LOGIN, json={"username": username, "password": password})
    assert login.status_code == 200

    token = login.json()["access_token"]
    me = client.get(ME, headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    assert me.json()["username"] == username


@pytest.mark.parametrize("username_ok", [True, False], ids=["wrong-password", "unknown-user"])
def test_bad_credentials_are_rejected_identically(
    client: TestClient, admin: tuple[str, str], username_ok: bool
) -> None:
    username = admin[0] if username_ok else "nobody"

    response = client.post(LOGIN, json={"username": username, "password": "wrong"})

    # Same status and message either way, so responses don't reveal which usernames exist.
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid username or password"}


@pytest.mark.parametrize(
    "authorization",
    [
        None,
        "Bearer not-a-jwt",
        "Bearer " + create_access_token("hr-admin", expires_in=timedelta(seconds=-1)),
    ],
    ids=["missing", "invalid", "expired"],
)
def test_protected_routes_reject_missing_invalid_or_expired_tokens(
    client: TestClient, admin: tuple[str, str], authorization: str | None
) -> None:
    headers = {"Authorization": authorization} if authorization else {}

    assert client.get(ME, headers=headers).status_code == 401
