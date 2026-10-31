"""Pay insights: one GROUP BY query each, in USD, over active employees only."""

from collections.abc import Sequence
from typing import Any

from sqlalchemy import Numeric, Select, cast, func, select
from sqlalchemy.orm import Session

from app.models import Country, Currency, Employee
from app.schemas.insights import CountryPay, Distribution, TitleInCountryPay, TitlePay
from app.services.conversion import CURRENCY_JOIN, SALARY_USD


def _usd(expression: Any) -> Any:
    """Round an aggregate to cents for display (percentile_cont returns a float)."""
    return func.round(cast(expression, Numeric), 2)


def _active(*columns: Any) -> Select[Any]:
    return select(*columns).join(Currency, CURRENCY_JOIN).where(Employee.is_active.is_(True))


def by_country(db: Session) -> list[CountryPay]:
    stmt = (
        _active(
            Country.code,
            Country.name,
            func.count(),
            _usd(func.min(SALARY_USD)),
            _usd(func.max(SALARY_USD)),
            _usd(func.avg(SALARY_USD)),
        )
        .join(Country, Country.code == Employee.country_code)
        .group_by(Country.code, Country.name)
        .order_by(Country.name)
    )
    return [
        CountryPay(
            country_code=code,
            country_name=name,
            headcount=headcount,
            min_usd=low,
            max_usd=high,
            avg_usd=avg,
        )
        for code, name, headcount, low, high, avg in db.execute(stmt)
    ]


def by_title(db: Session, country_code: str) -> list[TitlePay]:
    """Titles in a country, highest average first (so the first N are the top-paying)."""
    avg = _usd(func.avg(SALARY_USD))
    stmt = (
        _active(Employee.job_title, func.count(), avg)
        .where(Employee.country_code == country_code.upper())
        .group_by(Employee.job_title)
        .order_by(avg.desc(), Employee.job_title)
    )
    return [
        TitlePay(job_title=title, headcount=headcount, avg_usd=avg_usd)
        for title, headcount, avg_usd in db.execute(stmt)
    ]


def title_comparison(db: Session, job_title: str) -> list[TitleInCountryPay]:
    """One job title across countries, highest average first."""
    avg = _usd(func.avg(SALARY_USD))
    stmt = (
        _active(Country.code, Country.name, func.count(), avg)
        .join(Country, Country.code == Employee.country_code)
        .where(Employee.job_title == job_title)
        .group_by(Country.code, Country.name)
        .order_by(avg.desc(), Country.name)
    )
    return [
        TitleInCountryPay(country_code=code, country_name=name, headcount=headcount, avg_usd=a)
        for code, name, headcount, a in db.execute(stmt)
    ]


def distribution(db: Session, country_code: str) -> Distribution:
    code = country_code.upper()
    percentiles = [
        _usd(func.percentile_cont(p).within_group(SALARY_USD)) for p in (0.25, 0.5, 0.75, 0.9)
    ]
    stmt = _active(func.count(), *percentiles).where(Employee.country_code == code)
    headcount, p25, p50, p75, p90 = db.execute(stmt).one()
    return Distribution(
        country_code=code,
        headcount=headcount,
        p25_usd=p25,
        p50_usd=p50,
        p75_usd=p75,
        p90_usd=p90,
    )


def job_titles(db: Session) -> Sequence[str]:
    stmt = (
        select(Employee.job_title)
        .where(Employee.is_active.is_(True))
        .distinct()
        .order_by(Employee.job_title)
    )
    return db.scalars(stmt).all()
