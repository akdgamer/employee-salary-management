from fastapi import APIRouter, Depends
from sqlalchemy import select

from app.api.deps import DbSession, get_current_user
from app.models import Country, Currency
from app.schemas.lookup import CountryOut, CurrencyOut

router = APIRouter(tags=["lookups"], dependencies=[Depends(get_current_user)])


@router.get("/countries")
def list_countries(db: DbSession) -> list[CountryOut]:
    return [
        CountryOut.model_validate(c) for c in db.scalars(select(Country).order_by(Country.name))
    ]


@router.get("/currencies")
def list_currencies(db: DbSession) -> list[CurrencyOut]:
    return [
        CurrencyOut.model_validate(c) for c in db.scalars(select(Currency).order_by(Currency.code))
    ]
