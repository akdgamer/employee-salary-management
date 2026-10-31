import os
from collections.abc import Iterator
from pathlib import Path

import pytest

# Test settings must be in place before the app modules read them at import time.
os.environ.setdefault(
    "DATABASE_URL", "postgresql+psycopg://salary:salary@localhost:5434/salary_test"
)
os.environ.setdefault("JWT_SECRET", "test-secret-at-least-32-characters-long")
os.environ.setdefault("ADMIN_PASSWORD", "test-password")

from alembic import command  # noqa: E402
from alembic.config import Config  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import create_engine, text  # noqa: E402
from sqlalchemy.orm import Session  # noqa: E402

from app.core.db import get_db  # noqa: E402
from app.core.security import create_access_token  # noqa: E402
from app.main import app  # noqa: E402
from scripts.create_admin import create_admin  # noqa: E402
from scripts.seed import seed_lookups  # noqa: E402

BACKEND_DIR = Path(__file__).resolve().parents[1]

_engine = create_engine(os.environ["DATABASE_URL"])


def alembic_config(url: str) -> Config:
    config = Config(str(BACKEND_DIR / "alembic.ini"))
    config.set_main_option("sqlalchemy.url", url)
    return config


@pytest.fixture(scope="session", autouse=True)
def _schema() -> None:
    """Build the test schema from the migrations, exactly as production does."""
    with _engine.begin() as connection:
        connection.execute(text("DROP SCHEMA public CASCADE"))
        connection.execute(text("CREATE SCHEMA public"))
    command.upgrade(alembic_config(os.environ["DATABASE_URL"]), "head")


@pytest.fixture
def db() -> Iterator[Session]:
    """A session whose work is rolled back after each test.

    ``create_savepoint`` lets service code call ``rollback()`` (e.g. after an
    IntegrityError) without ending the outer transaction the fixture discards.
    """
    connection = _engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection, join_transaction_mode="create_savepoint")

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def admin(db: Session) -> tuple[str, str]:
    """The HR manager's login, created the same way production creates it."""
    username, password = "hr-admin", "correct-horse-battery"
    create_admin(db.connection(), username, password)
    return username, password


@pytest.fixture
def lookups(db: Session) -> None:
    """The real countries and currencies from the seed files."""
    seed_lookups(db.connection())


@pytest.fixture
def client(db: Session) -> Iterator[TestClient]:
    def _override_get_db() -> Iterator[Session]:
        yield db

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def auth_client(client: TestClient, admin: tuple[str, str], lookups: None) -> TestClient:
    """A client signed in as the HR manager, with lookups loaded."""
    client.headers["Authorization"] = f"Bearer {create_access_token(admin[0])}"
    return client
