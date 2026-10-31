from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Employee, SalaryHistory
from scripts.seed import country_currencies, seed


def test_seed_is_rerunnable_and_gives_every_employee_a_starting_salary(db: Session) -> None:
    conn = db.connection()

    seed(conn, n=200)
    seed(conn, n=200)  # a re-run must replace, not duplicate

    employees = db.scalars(select(Employee)).all()
    assert len(employees) == 200

    history = {h.employee_id: h for h in db.scalars(select(SalaryHistory))}
    assert len(history) == 200
    for employee in employees:
        start = history[employee.id]
        assert start.old_amount is None
        assert start.new_amount == employee.salary_amount
        assert start.currency == employee.salary_currency

    currency_of = country_currencies()
    assert all(e.salary_currency == currency_of[e.country_code] for e in employees)

    inactive = db.scalar(select(func.count()).where(Employee.is_active.is_(False)))
    assert inactive is not None and 0 < inactive < 200
