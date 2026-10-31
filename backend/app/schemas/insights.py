"""Pay insights. All amounts are USD and cover active employees only."""

from decimal import Decimal

from pydantic import BaseModel


class CountryPay(BaseModel):
    country_code: str
    country_name: str
    headcount: int
    min_usd: Decimal
    max_usd: Decimal
    avg_usd: Decimal


class TitlePay(BaseModel):
    job_title: str
    headcount: int
    avg_usd: Decimal


class TitleInCountryPay(BaseModel):
    country_code: str
    country_name: str
    headcount: int
    avg_usd: Decimal


class Distribution(BaseModel):
    """Percentiles are null when the country has no active employees."""

    country_code: str
    headcount: int
    p25_usd: Decimal | None
    p50_usd: Decimal | None
    p75_usd: Decimal | None
    p90_usd: Decimal | None
