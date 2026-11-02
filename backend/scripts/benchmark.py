"""Measure seeding and query performance on the seeded database.

Seeding is timed inside a transaction that is rolled back, so existing data is
left untouched. Queries run through the same service functions the API uses.

    python -m scripts.benchmark
"""

import statistics
import time
from collections.abc import Callable
from typing import Any

from sqlalchemy import func, select, text
from sqlalchemy.orm import Session

from app.core.db import SessionLocal, engine
from app.models import Employee
from app.services import employees, insights
from scripts.seed import copy_employees, insert_starting_history, seed_lookups

RUNS = 20


def timed(action: Callable[[], Any]) -> float:
    started = time.perf_counter()
    action()
    return (time.perf_counter() - started) * 1000


def median_ms(action: Callable[[], Any]) -> float:
    action()  # warm-up: connection, plan and page cache
    return statistics.median(timed(action) for _ in range(RUNS))


def benchmark_seed() -> list[tuple[str, float]]:
    with engine.connect() as conn, conn.begin() as transaction:
        stages = [
            ("Upsert countries and currencies", lambda: seed_lookups(conn)),
            (
                "Truncate employees and history",
                lambda: conn.execute(text("TRUNCATE salary_history, employees RESTART IDENTITY")),
            ),
            ("COPY 10,000 employees", lambda: copy_employees(conn, 10_000, seed=42)),
            ("Insert 10,000 starting-salary rows", lambda: insert_starting_history(conn)),
        ]
        results = [(name, timed(stage)) for name, stage in stages]
        transaction.rollback()
    return results + [("Total", sum(ms for _, ms in results))]


def benchmark_queries(db: Session) -> list[tuple[str, float]]:
    active = db.scalar(select(func.count()).where(Employee.is_active.is_(True))) or 0
    last_page = (active + 24) // 25
    cases: list[tuple[str, Callable[[], Any]]] = [
        ("List: first page, by name", lambda: employees.list_employees(db)),
        (
            "List: first page, by USD salary",
            lambda: employees.list_employees(db, sort="salary", order="desc"),
        ),
        ("List: search 'fischer'", lambda: employees.list_employees(db, search="fischer")),
        (f"List: last page ({last_page})", lambda: employees.list_employees(db, page=last_page)),
        ("Insights: by country", lambda: insights.by_country(db)),
        ("Insights: by title in US", lambda: insights.by_title(db, "US")),
        (
            "Insights: title across countries",
            lambda: insights.title_comparison(db, "Staff Engineer"),
        ),
        ("Insights: distribution in US", lambda: insights.distribution(db, "US")),
        ("Insights: job titles", lambda: insights.job_titles(db)),
    ]
    return [(name, median_ms(case)) for name, case in cases]


def print_table(title: str, rows: list[tuple[str, float]]) -> None:
    print(f"\n{title}\n")
    print("| Operation | Time (ms) |\n|---|---:|")
    for name, ms in rows:
        print(f"| {name} | {ms:.1f} |")


def main() -> None:
    print_table("Seed (single transaction, rolled back)", benchmark_seed())
    with SessionLocal() as db:
        print_table(f"Queries (median of {RUNS} warm runs)", benchmark_queries(db))


if __name__ == "__main__":
    main()
