import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import Settings


def test_health_returns_ok(client: TestClient) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_database_is_reachable(db: Session) -> None:
    assert db.execute(text("SELECT 1")).scalar_one() == 1


@pytest.mark.parametrize("missing", ["JWT_SECRET", "ADMIN_PASSWORD"])
def test_settings_require_secrets(missing: str, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv(missing)

    with pytest.raises(ValidationError, match=missing.lower()):
        Settings(_env_file=None)
