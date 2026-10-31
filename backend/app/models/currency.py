from datetime import date
from decimal import Decimal

from sqlalchemy import CHAR, Date, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class Currency(Base):
    """A currency with a static exchange rate snapshot (see decision 0001)."""

    __tablename__ = "currencies"

    code: Mapped[str] = mapped_column(CHAR(3), primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    rate_to_usd: Mapped[Decimal] = mapped_column(Numeric(20, 8))
    rates_as_of: Mapped[date] = mapped_column(Date)
