"""Employee business rules: listing, creation, updates and salary history."""

from collections.abc import Sequence
from decimal import Decimal
from typing import Any

from sqlalchemy import ColumnElement, Select, func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import Currency, Employee, SalaryHistory
from app.schemas.employee import (
    EmployeeCreate,
    EmployeeStatus,
    EmployeeUpdate,
    SortField,
    SortOrder,
)
from app.services.conversion import CURRENCY_JOIN, SALARY_USD

EmployeeRow = tuple[Employee, Decimal]
"""An employee with their salary converted to USD."""


class EmployeeNotFoundError(Exception):
    pass


class CurrencyChangeError(Exception):
    """An employee's salary currency is fixed after creation."""


class DuplicateError(Exception):
    def __init__(self, field: str) -> None:
        self.field = field


class UnknownReferenceError(Exception):
    def __init__(self, field: str) -> None:
        self.field = field


# Constraint names are deterministic (see the naming convention in app.core.db).
_CONSTRAINT_ERRORS: dict[str, Exception] = {
    "uq_employees_email": DuplicateError("email"),
    "fk_employees_country_code_countries": UnknownReferenceError("country_code"),
    "fk_employees_salary_currency_currencies": UnknownReferenceError("salary_currency"),
}

# Salary in USD (decision 0003): computed in SQL so sorting and paging use the same value.
_SALARY_USD = func.round(SALARY_USD, 2)

_SORT_COLUMNS: dict[SortField, Any] = {
    "name": Employee.full_name,
    "country": Employee.country_code,
    "salary": _SALARY_USD,
}


def _with_usd() -> Select[Employee, Decimal]:
    return select(Employee, _SALARY_USD).join(Currency, CURRENCY_JOIN)


def _escape_like(term: str) -> str:
    return term.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


def _filters(
    search: str | None, country: str | None, status: EmployeeStatus
) -> list[ColumnElement[bool]]:
    conditions: list[ColumnElement[bool]] = []
    if status != "all":
        conditions.append(Employee.is_active.is_(status == "active"))
    if country:
        conditions.append(Employee.country_code == country.upper())
    if search:
        pattern = f"%{_escape_like(search.strip())}%"
        conditions.append(
            or_(
                Employee.full_name.ilike(pattern, escape="\\"),
                Employee.email.ilike(pattern, escape="\\"),
                Employee.employee_code.ilike(pattern, escape="\\"),
            )
        )
    return conditions


def list_employees(
    db: Session,
    *,
    search: str | None = None,
    country: str | None = None,
    status: EmployeeStatus = "active",
    sort: SortField = "name",
    order: SortOrder = "asc",
    page: int = 1,
    page_size: int = 25,
) -> tuple[Sequence[EmployeeRow], int]:
    conditions = _filters(search, country, status)
    total = db.scalar(select(func.count()).select_from(Employee).where(*conditions)) or 0

    column = _SORT_COLUMNS[sort]
    direction = column.desc() if order == "desc" else column.asc()
    # id breaks ties (many employees share a name), so pages never overlap or skip.
    stmt = (
        _with_usd()
        .where(*conditions)
        .order_by(direction, Employee.id)
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    rows = [(employee, usd) for employee, usd in db.execute(stmt)]
    return rows, total


def get_employee(db: Session, employee_id: int) -> EmployeeRow:
    row = db.execute(_with_usd().where(Employee.id == employee_id)).one_or_none()
    if row is None:
        raise EmployeeNotFoundError
    return row[0], row[1]


def _flush(db: Session) -> None:
    """Flush pending writes, translating constraint violations into domain errors."""
    try:
        db.flush()
    except IntegrityError as exc:
        db.rollback()
        constraint = getattr(getattr(exc.orig, "diag", None), "constraint_name", None)
        if constraint in _CONSTRAINT_ERRORS:
            raise _CONSTRAINT_ERRORS[constraint] from exc
        raise


def create_employee(db: Session, data: EmployeeCreate) -> EmployeeRow:
    employee = Employee(**data.model_dump())
    db.add(employee)
    _flush(db)
    # Starting salary is the first history entry (decision 0005).
    db.add(
        SalaryHistory(
            employee_id=employee.id,
            old_amount=None,
            new_amount=employee.salary_amount,
            currency=employee.salary_currency,
        )
    )
    db.commit()
    return get_employee(db, employee.id)


def update_employee(db: Session, employee_id: int, data: EmployeeUpdate) -> EmployeeRow:
    employee = db.get(Employee, employee_id)
    if employee is None:
        raise EmployeeNotFoundError

    changes = data.model_dump(exclude_unset=True, exclude_none=True)
    currency = changes.pop("salary_currency", employee.salary_currency)
    if currency != employee.salary_currency:
        raise CurrencyChangeError

    new_salary = changes.get("salary_amount")
    if new_salary is not None and new_salary != employee.salary_amount:
        db.add(
            SalaryHistory(
                employee_id=employee.id,
                old_amount=employee.salary_amount,
                new_amount=new_salary,
                currency=employee.salary_currency,
            )
        )

    for field, value in changes.items():
        setattr(employee, field, value)
    _flush(db)
    db.commit()
    return get_employee(db, employee_id)


def salary_history(db: Session, employee_id: int) -> Sequence[SalaryHistory]:
    if db.get(Employee, employee_id) is None:
        raise EmployeeNotFoundError
    return db.scalars(
        select(SalaryHistory)
        .where(SalaryHistory.employee_id == employee_id)
        .order_by(SalaryHistory.changed_at.desc(), SalaryHistory.id.desc())
    ).all()
