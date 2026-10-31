from decimal import Decimal
from itertools import count

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models import Employee

INSIGHTS = "/api/v1/insights"
_ids = count()


def add(
    db: Session,
    salary: str,
    *,
    country: str = "US",
    currency: str = "USD",
    title: str = "Engineer",
    active: bool = True,
) -> None:
    n = next(_ids)
    db.add(
        Employee(
            full_name=f"Person {n}",
            email=f"person{n}@example.com",
            job_title=title,
            country_code=country,
            salary_amount=Decimal(salary),
            salary_currency=currency,
            is_active=active,
        )
    )
    db.flush()


@pytest.mark.parametrize(
    "path",
    [
        "/by-country",
        "/by-title?country=US",
        "/title-comparison?title=Engineer",
        "/distribution?country=US",
        "/job-titles",
    ],
)
def test_insights_require_login(client: TestClient, path: str) -> None:
    assert client.get(INSIGHTS + path).status_code == 401


def test_by_country_is_in_usd_and_ignores_inactive_employees(
    auth_client: TestClient, db: Session
) -> None:
    add(db, "100000")
    add(db, "200000")
    add(db, "999999", active=False)
    add(db, "2000000", country="IN", currency="INR")

    rows = {r["country_code"]: r for r in auth_client.get(f"{INSIGHTS}/by-country").json()}

    us = rows["US"]
    assert (us["headcount"], us["min_usd"], us["max_usd"], us["avg_usd"]) == (
        2,
        "100000.00",
        "200000.00",
        "150000.00",
    )
    assert rows["IN"]["avg_usd"] == "21062.56"  # 2,000,000 INR at the seeded rate


def test_distribution_percentiles(auth_client: TestClient, db: Session) -> None:
    for salary in ("10000", "20000", "30000", "40000", "50000"):
        add(db, salary)

    result = auth_client.get(f"{INSIGHTS}/distribution?country=US").json()
    empty = auth_client.get(f"{INSIGHTS}/distribution?country=SE").json()

    # Interpolated: p90 sits 60% of the way from 40k to 50k.
    assert (result["p25_usd"], result["p50_usd"], result["p75_usd"], result["p90_usd"]) == (
        "20000.00",
        "30000.00",
        "40000.00",
        "46000.00",
    )
    assert empty["headcount"] == 0 and empty["p50_usd"] is None


def test_titles_and_countries_are_ranked_by_average_pay(
    auth_client: TestClient, db: Session
) -> None:
    add(db, "100000", title="Designer")
    add(db, "120000", title="Engineer")
    add(db, "180000", title="Engineer")
    add(db, "2000000", country="IN", currency="INR", title="Engineer")

    by_title = auth_client.get(f"{INSIGHTS}/by-title?country=US").json()
    comparison = auth_client.get(f"{INSIGHTS}/title-comparison?title=Engineer").json()

    assert [(t["job_title"], t["avg_usd"]) for t in by_title] == [
        ("Engineer", "150000.00"),
        ("Designer", "100000.00"),
    ]
    assert [c["country_code"] for c in comparison] == ["US", "IN"]
