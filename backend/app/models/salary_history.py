from datetime import datetime
from decimal import Decimal

from sqlalchemy import CHAR, CheckConstraint, DateTime, ForeignKey, Index, Numeric, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class SalaryHistory(Base):
    """One salary change. ``old_amount`` is null for the starting salary."""

    __tablename__ = "salary_history"

    id: Mapped[int] = mapped_column(primary_key=True)
    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id", ondelete="RESTRICT"))
    old_amount: Mapped[Decimal | None] = mapped_column(Numeric(14, 2))
    new_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    currency: Mapped[str] = mapped_column(CHAR(3), ForeignKey("currencies.code"))
    changed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        CheckConstraint("new_amount > 0", name="new_amount_positive"),
        Index("ix_salary_history_employee_changed", "employee_id", "changed_at"),
    )
