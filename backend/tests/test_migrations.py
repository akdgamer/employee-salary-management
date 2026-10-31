import os
from collections.abc import Iterator
from pathlib import Path

import pytest
from alembic import command
from alembic.autogenerate import compare_metadata
from alembic.config import Config
from alembic.migration import MigrationContext
from sqlalchemy import create_engine, make_url, text
from sqlalchemy.engine import URL

from app.core.db import Base

BACKEND_DIR = Path(__file__).resolve().parents[1]


@pytest.fixture
def empty_database_url() -> Iterator[URL]:
    """A throwaway database, so migrations run on a truly empty schema."""
    test_url = make_url(os.environ["DATABASE_URL"])
    scratch_url = test_url.set(database="salary_migrations_check")
    admin = create_engine(test_url, isolation_level="AUTOCOMMIT")
    with admin.connect() as connection:
        connection.execute(text("DROP DATABASE IF EXISTS salary_migrations_check"))
        connection.execute(text("CREATE DATABASE salary_migrations_check"))
    yield scratch_url
    with admin.connect() as connection:
        connection.execute(text("DROP DATABASE IF EXISTS salary_migrations_check WITH (FORCE)"))
    admin.dispose()


def test_migrations_match_models(empty_database_url: URL) -> None:
    """Tests build tables from the models; production builds them from migrations.

    If the two drift apart, tests pass while production breaks.
    """
    config = Config(str(BACKEND_DIR / "alembic.ini"))
    config.set_main_option(
        "sqlalchemy.url", empty_database_url.render_as_string(hide_password=False)
    )

    command.upgrade(config, "head")

    engine = create_engine(empty_database_url)
    with engine.connect() as connection:
        diff = compare_metadata(MigrationContext.configure(connection), Base.metadata)
    engine.dispose()

    assert diff == []
