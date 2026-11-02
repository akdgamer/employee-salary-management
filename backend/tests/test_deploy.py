import pytest
from sqlalchemy import func, select, update
from sqlalchemy.orm import Session

from app.core.config import Settings
from app.models import Employee, User
from scripts.prestart import prepare_data


def test_redeploy_keeps_existing_data_and_refreshes_admin_password(db: Session) -> None:
    conn = db.connection()
    assert prepare_data(conn, "hr", "first-password", n=50) is True

    conn.execute(update(Employee).where(Employee.id == 1).values(job_title="Edited by HR"))
    assert prepare_data(conn, "hr", "rotated-password", n=50) is False

    assert db.scalar(select(func.count()).select_from(Employee)) == 50
    assert db.get(Employee, 1).job_title == "Edited by HR"  # type: ignore[union-attr]
    assert db.scalar(select(func.count()).select_from(User)) == 1


@pytest.mark.parametrize(
    "given",
    ["postgres://u:p@db.example.com/app", "postgresql://u:p@db.example.com/app"],
)
def test_provider_database_urls_use_the_psycopg_driver(given: str) -> None:
    settings = Settings(_env_file=None, database_url=given)

    assert settings.database_url == "postgresql+psycopg://u:p@db.example.com/app"
