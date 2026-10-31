"""Create the HR manager's login, or reset its password if it already exists.

Reads ADMIN_USERNAME and ADMIN_PASSWORD from settings. Never touches employee data,
so it is safe to run in production to rotate the password.

    python -m scripts.create_admin
"""

from sqlalchemy import Connection
from sqlalchemy.dialects.postgresql import insert

from app.core.config import get_settings
from app.core.db import engine
from app.core.security import hash_password
from app.models import User


def create_admin(conn: Connection, username: str, password: str) -> None:
    stmt = insert(User).values(username=username, password_hash=hash_password(password))
    conn.execute(
        stmt.on_conflict_do_update(
            index_elements=["username"], set_={"password_hash": stmt.excluded.password_hash}
        )
    )


def main() -> None:
    settings = get_settings()
    with engine.begin() as conn:
        create_admin(conn, settings.admin_username, settings.admin_password)
    print(f"Admin user '{settings.admin_username}' is ready")


if __name__ == "__main__":
    main()
