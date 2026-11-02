# Performance

Measured with `python -m scripts.benchmark` (from `backend/`) on the seeded dataset: 10,000 employees, 9,477 active. Environment: PostgreSQL 16 in Docker on a developer laptop. Query times include the service layer and ORM but not HTTP. Rerun the script to reproduce; absolute numbers vary by machine.

## Seeding

One transaction (the benchmark rolls it back, so data is untouched):

| Stage | Time |
|---|---:|
| Upsert countries and currencies | 7 ms |
| Truncate employees and history | 22 ms |
| `COPY` 10,000 employees | 290 ms |
| Insert 10,000 starting-salary history rows | 184 ms |
| **Total** | **~0.5 s** |

`COPY` streams generated rows straight into the table instead of one `INSERT` round trip per row (decision 0006). The history insert is a single `INSERT … SELECT`; most of its time is foreign-key checks and index maintenance.

## Queries

Median of 20 warm runs:

| Operation | Time |
|---|---:|
| Employee list, first page, sorted by name | 5.6 ms |
| Employee list, first page, sorted by USD salary | 6.0 ms |
| Employee list, search "fischer" | 16.6 ms |
| Employee list, last page (380) | 10.0 ms |
| Insights: pay by country | 6.1 ms |
| Insights: by title in the US | 2.1 ms |
| Insights: one title across countries | 1.9 ms |
| Insights: distribution in the US (`percentile_cont`) | 5.0 ms |
| Insights: job titles | 1.3 ms |

Everything is well inside interactive latency, so there is no caching layer. At this size, caching would add invalidation problems without a visible benefit.

## Index usage

From `EXPLAIN ANALYZE` on the seeded data:

- **Per-country insights** use `ix_employees_active_country_title` (an index scan for a small country such as Sweden, 0.8 ms; a bitmap scan for the 3,388 active US employees, 2.0 ms).
- **Salary history** for one employee uses `ix_salary_history_employee_changed` backwards: newest first with no sort step.
- **Search** is a sequential scan, because `ILIKE '%term%'` with a leading wildcard can't use a B-tree index. At 10,000 rows it takes 8.5 ms in the database, which is acceptable.

## What changes at larger scale

| At | Bottleneck | Change |
|---|---|---|
| ~100k employees | Search scans every row | `pg_trgm` GIN index on name and email |
| ~1M employees | `OFFSET` pagination reads and discards every earlier row; `COUNT(*)` for the total on each page | Keyset pagination (continue after the last sort value + `id`); approximate or cached totals |
| ~1M employees | Insights re-aggregate all active employees per request | Pre-aggregated tables or materialised views, refreshed on salary change or on a schedule |
| Live exchange rates | Static rates make results reproducible | A scheduled job updating `rate_to_usd` (decision 0001); query code is unchanged |

## Frontend

Production build (Vite):

| Chunk | Size | Gzipped |
|---|---:|---:|
| Shared (React, MUI, router, query client, sign-in) | 695 kB | 221 kB |
| Employees page (incl. data grid) | 508 kB | 148 kB |
| Insights page (incl. charts) | 364 kB | 105 kB |

Pages are lazy-loaded, so the sign-in page doesn't download the grid or the charts. The remaining shared chunk is mostly MUI. Splitting it further with manual vendor chunks is possible, but gains little for an internal tool used on desktop.

Lists keep the previous page on screen while the next loads, search is debounced (300 ms), and lookups (countries, currencies) are fetched once per session.

## Hosting (free tiers)

- **Render** sleeps the API after 15 minutes without traffic; the next request takes about a minute.
- **Neon** suspends the database after 5 minutes idle and resumes on the next query. `pool_pre_ping` discards connections that went stale during suspension.

After the first request, the live app responds at the speeds above plus network latency.
