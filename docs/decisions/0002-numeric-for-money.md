# 0002: `NUMERIC` for money, never floating point

**Status:** Accepted · **Date:** 2026-10-31

## Context
Binary floating point cannot represent most decimal amounts exactly, so sums and conversions drift by fractions of a cent. In salary data that shows up as totals that do not reconcile.

## Decision
- Salaries: `NUMERIC(14,2)`. Exchange rates: `NUMERIC(20,8)`.
- Python uses `decimal.Decimal` end to end.
- The API serialises money as decimal strings (e.g. `"125000.00"`), not JSON numbers.

## Consequences
- **+** All arithmetic in the database and the service layer is exact.
- **+** No precision loss when JSON is parsed in the browser.
- **−** The frontend must treat money as strings and format them explicitly.
