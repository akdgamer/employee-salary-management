from sqlalchemy import CHAR, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class Country(Base):
    __tablename__ = "countries"

    code: Mapped[str] = mapped_column(CHAR(2), primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
