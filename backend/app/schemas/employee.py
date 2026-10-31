from datetime import datetime
from decimal import Decimal
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, StringConstraints

Name = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=200)]
JobTitle = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=120)]
CountryCode = Annotated[str, StringConstraints(to_upper=True, pattern=r"^[A-Za-z]{2}$")]
CurrencyCode = Annotated[str, StringConstraints(to_upper=True, pattern=r"^[A-Za-z]{3}$")]
Money = Annotated[Decimal, Field(gt=0, max_digits=14, decimal_places=2)]

EmployeeStatus = Literal["active", "inactive", "all"]
SortField = Literal["name", "country", "salary"]
SortOrder = Literal["asc", "desc"]


class EmployeeCreate(BaseModel):
    full_name: Name
    email: EmailStr
    job_title: JobTitle
    country_code: CountryCode
    salary_amount: Money
    salary_currency: CurrencyCode


class EmployeeUpdate(BaseModel):
    """Partial update. ``salary_currency`` may be sent but must not change."""

    full_name: Name | None = None
    email: EmailStr | None = None
    job_title: JobTitle | None = None
    country_code: CountryCode | None = None
    salary_amount: Money | None = None
    salary_currency: CurrencyCode | None = None
    is_active: bool | None = None


class EmployeeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    employee_code: str
    full_name: str
    email: str
    job_title: str
    country_code: str
    salary_amount: Decimal
    salary_currency: str
    salary_usd: Decimal
    is_active: bool
    created_at: datetime
    updated_at: datetime


class EmployeePage(BaseModel):
    items: list[EmployeeOut]
    total: int
    page: int
    page_size: int


class SalaryChangeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    old_amount: Decimal | None
    new_amount: Decimal
    currency: str
    changed_at: datetime
