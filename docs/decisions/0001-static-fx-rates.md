# 0001: Static exchange rates

**Status:** Accepted · **Date:** 2026-10-31

## Context
Employees are paid in their local currencies. Comparing pay across countries, sorting by salary and computing cross-country aggregates all need a common unit.

## Decision
Store a static snapshot of exchange rates in the `currencies` table (`rate_to_usd`, `rates_as_of`), loaded from a versioned seed file. Do not call a live rate provider.

## Consequences
- **+** No external dependency: deployments and tests run offline and deterministically.
- **+** Aggregates are reproducible; the same data always yields the same insights.
- **−** Rates drift. The UI shows `rates_as_of` so converted figures are read as indicative.
- **Migration path:** `rate_to_usd` is the only contract queries depend on. A scheduled job that refreshes it would switch to live rates without changing services or routes.
