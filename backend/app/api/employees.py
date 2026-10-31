from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.deps import DbSession, get_current_user
from app.schemas.employee import (
    EmployeeCreate,
    EmployeeOut,
    EmployeePage,
    EmployeeStatus,
    EmployeeUpdate,
    SalaryChangeOut,
    SortField,
    SortOrder,
)
from app.services import employees as service
from app.services.employees import EmployeeRow

router = APIRouter(
    prefix="/employees", tags=["employees"], dependencies=[Depends(get_current_user)]
)


def _out(row: EmployeeRow) -> EmployeeOut:
    employee, salary_usd = row
    fields = (name for name in EmployeeOut.model_fields if name != "salary_usd")
    return EmployeeOut.model_validate(
        {**{name: getattr(employee, name) for name in fields}, "salary_usd": salary_usd}
    )


def _not_found() -> HTTPException:
    return HTTPException(status.HTTP_404_NOT_FOUND, detail="Employee not found")


def _invalid(exc: Exception) -> HTTPException:
    if isinstance(exc, service.DuplicateError):
        return HTTPException(status.HTTP_409_CONFLICT, detail=f"{exc.field} already exists")
    if isinstance(exc, service.UnknownReferenceError):
        return HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, detail=f"Unknown {exc.field}")
    return HTTPException(
        status.HTTP_422_UNPROCESSABLE_CONTENT, detail="Salary currency cannot be changed"
    )


@router.get("")
def list_employees(
    db: DbSession,
    search: str | None = None,
    country: str | None = None,
    status_: Annotated[EmployeeStatus, Query(alias="status")] = "active",
    sort: SortField = "name",
    order: SortOrder = "asc",
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 25,
) -> EmployeePage:
    rows, total = service.list_employees(
        db,
        search=search,
        country=country,
        status=status_,
        sort=sort,
        order=order,
        page=page,
        page_size=page_size,
    )
    return EmployeePage(
        items=[_out(row) for row in rows], total=total, page=page, page_size=page_size
    )


@router.post("", status_code=status.HTTP_201_CREATED)
def create_employee(payload: EmployeeCreate, db: DbSession) -> EmployeeOut:
    try:
        return _out(service.create_employee(db, payload))
    except (service.DuplicateError, service.UnknownReferenceError) as exc:
        raise _invalid(exc) from exc


@router.get("/{employee_id}")
def get_employee(employee_id: int, db: DbSession) -> EmployeeOut:
    try:
        return _out(service.get_employee(db, employee_id))
    except service.EmployeeNotFoundError as exc:
        raise _not_found() from exc


@router.patch("/{employee_id}")
def update_employee(employee_id: int, payload: EmployeeUpdate, db: DbSession) -> EmployeeOut:
    try:
        return _out(service.update_employee(db, employee_id, payload))
    except service.EmployeeNotFoundError as exc:
        raise _not_found() from exc
    except (
        service.DuplicateError,
        service.UnknownReferenceError,
        service.CurrencyChangeError,
    ) as exc:
        raise _invalid(exc) from exc


@router.get("/{employee_id}/salary-history")
def salary_history(employee_id: int, db: DbSession) -> list[SalaryChangeOut]:
    try:
        return [SalaryChangeOut.model_validate(h) for h in service.salary_history(db, employee_id)]
    except service.EmployeeNotFoundError as exc:
        raise _not_found() from exc
