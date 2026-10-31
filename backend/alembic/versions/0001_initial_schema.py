"""Initial schema: countries, currencies, users, employees, salary_history.

Revision ID: 0001
Revises:
Create Date: 2026-10-31
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS citext")

    op.create_table(
        "countries",
        sa.Column("code", sa.CHAR(2), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.PrimaryKeyConstraint("code", name=op.f("pk_countries")),
    )
    op.create_table(
        "currencies",
        sa.Column("code", sa.CHAR(3), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("rate_to_usd", sa.Numeric(20, 8), nullable=False),
        sa.Column("rates_as_of", sa.Date(), nullable=False),
        sa.PrimaryKeyConstraint("code", name=op.f("pk_currencies")),
    )
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("username", sa.String(64), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_users")),
        sa.UniqueConstraint("username", name=op.f("uq_users_username")),
    )
    op.create_table(
        "employees",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("employee_code", sa.String(32), nullable=False),
        sa.Column("full_name", sa.String(200), nullable=False),
        sa.Column("email", postgresql.CITEXT(), nullable=False),
        sa.Column("job_title", sa.String(120), nullable=False),
        sa.Column("country_code", sa.CHAR(2), nullable=False),
        sa.Column("salary_amount", sa.Numeric(14, 2), nullable=False),
        sa.Column("salary_currency", sa.CHAR(3), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint("salary_amount > 0", name=op.f("ck_employees_salary_amount_positive")),
        sa.ForeignKeyConstraint(
            ["country_code"], ["countries.code"], name=op.f("fk_employees_country_code_countries")
        ),
        sa.ForeignKeyConstraint(
            ["salary_currency"],
            ["currencies.code"],
            name=op.f("fk_employees_salary_currency_currencies"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_employees")),
        sa.UniqueConstraint("email", name=op.f("uq_employees_email")),
        sa.UniqueConstraint("employee_code", name=op.f("uq_employees_employee_code")),
    )
    op.create_index(
        "ix_employees_active_country_title",
        "employees",
        ["is_active", "country_code", "job_title"],
    )
    op.create_table(
        "salary_history",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("employee_id", sa.Integer(), nullable=False),
        sa.Column("old_amount", sa.Numeric(14, 2), nullable=True),
        sa.Column("new_amount", sa.Numeric(14, 2), nullable=False),
        sa.Column("currency", sa.CHAR(3), nullable=False),
        sa.Column(
            "changed_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint("new_amount > 0", name=op.f("ck_salary_history_new_amount_positive")),
        sa.ForeignKeyConstraint(
            ["currency"], ["currencies.code"], name=op.f("fk_salary_history_currency_currencies")
        ),
        sa.ForeignKeyConstraint(
            ["employee_id"],
            ["employees.id"],
            name=op.f("fk_salary_history_employee_id_employees"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_salary_history")),
    )
    op.create_index(
        "ix_salary_history_employee_changed",
        "salary_history",
        ["employee_id", "changed_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_salary_history_employee_changed", table_name="salary_history")
    op.drop_table("salary_history")
    op.drop_index("ix_employees_active_country_title", table_name="employees")
    op.drop_table("employees")
    op.drop_table("users")
    op.drop_table("currencies")
    op.drop_table("countries")
    op.execute("DROP EXTENSION IF EXISTS citext")
