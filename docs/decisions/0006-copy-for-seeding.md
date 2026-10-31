# 0006: PostgreSQL `COPY` for the seed script

**Status:** Accepted · **Date:** 2026-10-31

## Context
The seed script loads 10,000 employees plus their starting-salary history rows. It is re-run often during development, testing and demos, so it must be fast and repeatable.

## Decision
- Stream generated rows into PostgreSQL with `COPY FROM STDIN` (via `psycopg`), not row-by-row `INSERT`.
- Use a fixed random seed so every run produces the same data.
- Truncate employee data before loading so re-runs replace rather than duplicate.

## Consequences
- **+** Bulk loading avoids a network round trip per row. Measured timings will be recorded in the performance notes.
- **+** Deterministic data: the demo, the tests and every reviewer see the same employees.
- **−** `COPY` bypasses the application layer, so the script must write `salary_history` rows itself (see [0005](0005-salary-history-in-application.md)).
- **−** PostgreSQL-specific; part of the reason for choosing PostgreSQL.
