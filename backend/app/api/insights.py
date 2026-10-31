from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.api.deps import DbSession, get_current_user
from app.schemas.insights import CountryPay, Distribution, TitleInCountryPay, TitlePay
from app.services import insights as service

router = APIRouter(prefix="/insights", tags=["insights"], dependencies=[Depends(get_current_user)])

CountryParam = Annotated[str, Query(pattern=r"^[A-Za-z]{2}$")]


@router.get("/by-country")
def by_country(db: DbSession) -> list[CountryPay]:
    return service.by_country(db)


@router.get("/by-title")
def by_title(country: CountryParam, db: DbSession) -> list[TitlePay]:
    return service.by_title(db, country)


@router.get("/title-comparison")
def title_comparison(
    title: Annotated[str, Query(min_length=1)], db: DbSession
) -> list[TitleInCountryPay]:
    return service.title_comparison(db, title)


@router.get("/distribution")
def distribution(country: CountryParam, db: DbSession) -> Distribution:
    return service.distribution(db, country)


@router.get("/job-titles")
def job_titles(db: DbSession) -> list[str]:
    return list(service.job_titles(db))
