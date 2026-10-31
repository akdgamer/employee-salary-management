# 0003: Convert to USD in SQL

**Status:** Accepted · **Date:** 2026-10-31

## Context
Salaries are stored in local currency (the contractual amount). The employee table sorts by salary across currencies, and every insight aggregates across currencies. Conversion could happen in the database, in Python after the query, or in the browser.

## Decision
Convert in SQL by joining `currencies` and computing `salary_amount × rate_to_usd` inside the query. All converted figures and insights are in USD.

## Consequences
- **+** Sorting and pagination are correct: the database orders the full dataset by the USD amount *before* `LIMIT/OFFSET`. Converting in Python or the browser would only sort the current page.
- **+** Aggregates (`AVG`, `percentile_cont`) run on comparable values in one query, with exact `NUMERIC` arithmetic.
- **+** One place defines conversion, so the table and insights cannot disagree.
- **−** USD only. A display-currency selector (deferred) would extend the expression to `× rate_to_usd(local) ÷ rate_to_usd(target)`.
