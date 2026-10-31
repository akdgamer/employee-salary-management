import os
from collections.abc import Iterator

import pytest

# Test settings must be in place before the app modules read them at import time.
os.environ.setdefault(
    "DATABASE_URL", "postgresql+psycopg://salary:salary@localhost:5434/salary_test"
)
os.environ.setdefault("JWT_SECRET", "test-secret-at-least-32-characters-long")
os.environ.setdefault("ADMIN_PASSWORD", "test-password")

from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import create_engine  # noqa: E402
from sqlalchemy.orm import Session  # noqa: E402

from app.core.db import Base, get_db  # noqa: E402
from app.main import app  # noqa: E402

_engine = create_engine(os.environ["DATABASE_URL"])


@pytest.fixture(scope="session", autouse=True)
def _schema() -> Iterator[None]:
    Base.metadata.drop_all(_engine)
    Base.metadata.create_all(_engine)
    yield
    Base.metadata.drop_all(_engine)


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
def client(db: Session) -> Iterator[TestClient]:
    def _override_get_db() -> Iterator[Session]:
        yield db

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
