# 0005: Write salary history in the application, not a database trigger

**Status:** Accepted · **Date:** 2026-10-31

## Context
Every salary change must leave a history row (old amount, new amount, currency, time). Two options:
1. **Database trigger:** fires on any `UPDATE` of `salary_amount`, including direct SQL.
2. **Application code:** the employee service inserts the history row in the same transaction as the update.

## Decision
Application code. The service that creates or updates an employee writes the `salary_history` row inside the same transaction:
- On create: a row with `old_amount = NULL` and the starting salary.
- On update: a row only when `salary_amount` actually changes.

## Consequences
- **+** The rule is plain Python, visible next to the update logic, and covered by fast unit tests.
- **+** Same transaction: the salary and its history row are saved together or not at all.
- **−** Writes that bypass the service (manual SQL, bulk loads) do not record history. Acceptable because all changes go through the API. The seed script therefore writes starting-salary rows itself.
- **Revisit if:** other systems start writing to the database directly. A trigger would then be the safer guarantee.
