"""Prepare the database before the API starts (run by the container on every deploy).

1. Apply migrations.
2. Create the HR manager's login, or reset its password from the environment.
3. Load lookups, and seed employees only if there are none, so a redeploy
   never overwrites data HR has edited.

    python -m scripts.prestart
"""

from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import Connection, func, select

from app.core.config import get_settings
from app.core.db import engine
from app.models import Employee
from scripts.create_admin import create_admin
from scripts.seed import seed_employees, seed_lookups

ALEMBIC_INI = Path(__file__).resolve().parents[1] / "alembic.ini"


def prepare_data(conn: Connection, admin_username: str, admin_password: str, n: int) -> bool:
    """Returns True if employees were seeded."""
    create_admin(conn, admin_username, admin_password)
    seed_lookups(conn)
    if conn.scalar(select(func.count()).select_from(Employee)):
        return False
    seed_employees(conn, n, seed=42)
    return True


def main() -> None:
    settings = get_settings()
    command.upgrade(Config(str(ALEMBIC_INI)), "head")
    with engine.begin() as conn:
        seeded = prepare_data(conn, settings.admin_username, settings.admin_password, n=10_000)
    print("Seeded 10,000 employees" if seeded else "Employees present; seed skipped")


if __name__ == "__main__":
    main()
