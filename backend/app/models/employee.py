from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    CHAR,
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Numeric,
    String,
    func,
    true,
)
from sqlalchemy.dialects.postgresql import CITEXT
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class Employee(Base):
    """An employee and their current salary in local currency.

    Employees are deactivated, never deleted (see decision 0004).
    """

    __tablename__ = "employees"

    id: Mapped[int] = mapped_column(primary_key=True)
    employee_code: Mapped[str] = mapped_column(String(32), unique=True)
    full_name: Mapped[str] = mapped_column(String(200))
    email: Mapped[str] = mapped_column(CITEXT, unique=True)
    job_title: Mapped[str] = mapped_column(String(120))
    country_code: Mapped[str] = mapped_column(CHAR(2), ForeignKey("countries.code"))
    salary_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    salary_currency: Mapped[str] = mapped_column(CHAR(3), ForeignKey("currencies.code"))
    is_active: Mapped[bool] = mapped_column(Boolean, server_default=true())
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    __table_args__ = (
        CheckConstraint("salary_amount > 0", name="salary_amount_positive"),
        Index("ix_employees_active_country_title", "is_active", "country_code", "job_title"),
    )
