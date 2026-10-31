"""Generate employee codes from a sequence.

Revision ID: 0002
Revises: 0001
Create Date: 2026-10-31
"""

from collections.abc import Sequence

from alembic import op

revision: str = "0002"
down_revision: str | None = "0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Owned by the column, so TRUNCATE ... RESTART IDENTITY resets it with the table.
    op.execute("CREATE SEQUENCE employee_code_seq OWNED BY employees.employee_code")
    # Continue after any existing EMP-nnnnnn codes.
    op.execute(
        "SELECT setval('employee_code_seq', COALESCE(MAX(substring(employee_code FROM 5)::int), 0)"
        " + 1, false) FROM employees WHERE employee_code ~ '^EMP-[0-9]+$'"
    )
    op.execute(
        "ALTER TABLE employees ALTER COLUMN employee_code"
        " SET DEFAULT 'EMP-' || lpad(nextval('employee_code_seq')::text, 6, '0')"
    )


def downgrade() -> None:
    op.execute("ALTER TABLE employees ALTER COLUMN employee_code DROP DEFAULT")
    op.execute("DROP SEQUENCE employee_code_seq")
