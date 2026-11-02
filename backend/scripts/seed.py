"""Seed the database with lookups and 10,000 deterministic employees.

Re-runnable: lookups are upserted, employees and their history are replaced.

    python -m scripts.seed
"""

import json
import random
import time
from collections.abc import Iterator
from datetime import date
from decimal import Decimal
from pathlib import Path
from typing import Any

from sqlalchemy import Connection, text
from sqlalchemy.dialects.postgresql import insert

from app.core.config import get_settings
from app.core.db import engine
from app.models import Country, Currency
from scripts.create_admin import create_admin

SEED_DIR = Path(__file__).resolve().parent / "seed_data"

INACTIVE_SHARE = 0.05

COUNTRY_WEIGHTS = {
    "US": 35,
    "IN": 20,
    "GB": 10,
    "DE": 6,
    "FR": 5,
    "CA": 4,
    "JP": 4,
    "AU": 3,
    "BR": 3,
    "SG": 2,
    "NL": 2,
    "MX": 2,
    "AE": 2,
    "SE": 1,
    "ZA": 1,
}

# Annual base salary range per country, in local currency.
COUNTRY_SALARY_RANGE = {
    "US": (60_000, 220_000),
    "GB": (40_000, 160_000),
    "IN": (600_000, 4_000_000),
    "DE": (50_000, 150_000),
    "FR": (45_000, 130_000),
    "JP": (5_000_000, 18_000_000),
    "CA": (55_000, 160_000),
    "AU": (60_000, 180_000),
    "BR": (60_000, 250_000),
    "ZA": (300_000, 1_200_000),
    "MX": (200_000, 900_000),
    "SG": (60_000, 220_000),
    "AE": (120_000, 500_000),
    "NL": (50_000, 140_000),
    "SE": (450_000, 1_300_000),
}

# Multiplier range applied to the country's base range.
TITLE_MULTIPLIER = {
    "Software Engineer": (0.8, 1.1),
    "Senior Software Engineer": (1.1, 1.6),
    "Staff Engineer": (1.5, 2.2),
    "Engineering Manager": (1.3, 1.9),
    "Product Manager": (1.0, 1.6),
    "Data Analyst": (0.7, 1.0),
    "Data Scientist": (1.0, 1.5),
    "Designer": (0.8, 1.2),
    "Customer Support": (0.4, 0.7),
    "Sales Representative": (0.6, 1.0),
    "Account Executive": (0.9, 1.4),
    "Marketing Manager": (0.9, 1.3),
    "Operations Lead": (0.9, 1.3),
    "HR Manager": (0.9, 1.3),
    "Finance Analyst": (0.8, 1.2),
    "Recruiter": (0.6, 0.9),
    "QA Engineer": (0.7, 1.0),
    "DevOps Engineer": (1.0, 1.5),
    "Security Engineer": (1.1, 1.6),
    "Solutions Architect": (1.2, 1.7),
}

# employee_code is omitted: the database generates it from employee_code_seq.
EMPLOYEE_COLUMNS = (
    "full_name",
    "email",
    "job_title",
    "country_code",
    "salary_amount",
    "salary_currency",
    "is_active",
)


def load_json(name: str) -> Any:
    return json.loads((SEED_DIR / name).read_text())


def country_currencies() -> dict[str, str]:
    """Country code -> the currency its employees are paid in."""
    return {country["code"]: country["currency"] for country in load_json("countries.json")}


def seed_lookups(conn: Connection) -> None:
    """Upsert countries and currencies so edits to the seed files take effect on re-run."""
    countries = [{"code": c["code"], "name": c["name"]} for c in load_json("countries.json")]
    stmt = insert(Country).values(countries)
    conn.execute(
        stmt.on_conflict_do_update(index_elements=["code"], set_={"name": stmt.excluded.name})
    )

    snapshot = load_json("currencies.json")
    as_of = date.fromisoformat(snapshot["as_of"])
    currencies = [
        {
            "code": c["code"],
            "name": c["name"],
            "rate_to_usd": Decimal(c["rate_to_usd"]),
            "rates_as_of": as_of,
        }
        for c in snapshot["currencies"]
    ]
    stmt = insert(Currency).values(currencies)
    conn.execute(
        stmt.on_conflict_do_update(
            index_elements=["code"],
            set_={
                "name": stmt.excluded.name,
                "rate_to_usd": stmt.excluded.rate_to_usd,
                "rates_as_of": stmt.excluded.rates_as_of,
            },
        )
    )


def generate_employees(rng: random.Random, n: int) -> Iterator[tuple[object, ...]]:
    first_names = (SEED_DIR / "first_names.txt").read_text().split()
    last_names = (SEED_DIR / "last_names.txt").read_text().split()
    currency_of = country_currencies()
    countries = list(COUNTRY_WEIGHTS)
    weights = list(COUNTRY_WEIGHTS.values())
    titles = list(TITLE_MULTIPLIER)

    for i in range(1, n + 1):
        first, last = rng.choice(first_names), rng.choice(last_names)
        country = rng.choices(countries, weights=weights)[0]
        title = rng.choice(titles)
        low, high = COUNTRY_SALARY_RANGE[country]
        m_low, m_high = TITLE_MULTIPLIER[title]
        salary = Decimal(f"{rng.uniform(low * m_low, high * m_high):.2f}")
        is_active = rng.random() >= INACTIVE_SHARE
        yield (
            f"{first} {last}",
            f"{first.lower()}.{last.lower()}.{i}@example.com",
            title,
            country,
            salary,
            currency_of[country],
            is_active,
        )


def copy_employees(conn: Connection, n: int, seed: int) -> None:
    """Bulk-load generated employees; COPY runs on the same transaction as `conn`."""
    cursor = conn.connection.driver_connection.cursor()  # type: ignore[union-attr]
    with cursor.copy(f"COPY employees ({', '.join(EMPLOYEE_COLUMNS)}) FROM STDIN") as copy:
        for row in generate_employees(random.Random(seed), n):
            copy.write_row(row)


def insert_starting_history(conn: Connection) -> None:
    """COPY skips the service layer, so the starting-salary history is written here (ADR 0005)."""
    conn.execute(
        text(
            "INSERT INTO salary_history"
            " (employee_id, old_amount, new_amount, currency, changed_at)"
            " SELECT id, NULL, salary_amount, salary_currency, created_at FROM employees"
        )
    )


def seed_employees(conn: Connection, n: int, seed: int) -> None:
    """Replace all employees and give each one a starting-salary history row."""
    conn.execute(text("TRUNCATE salary_history, employees RESTART IDENTITY"))
    copy_employees(conn, n, seed)
    insert_starting_history(conn)


def seed(conn: Connection, n: int = 10_000, random_seed: int = 42) -> None:
    seed_lookups(conn)
    seed_employees(conn, n, random_seed)


def main() -> None:
    settings = get_settings()
    started = time.perf_counter()
    with engine.begin() as conn:
        seed(conn)
        create_admin(conn, settings.admin_username, settings.admin_password)
    elapsed = time.perf_counter() - started
    print(f"Seeded 10,000 employees with salary history in {elapsed:.2f}s")


if __name__ == "__main__":
    main()
