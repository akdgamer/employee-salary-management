# 0004: Deactivate employees instead of deleting them

**Status:** Accepted · **Date:** 2026-10-31

## Context
When someone leaves, HR still needs their past pay data and salary history. A hard delete would remove both, or would leave orphaned history rows.

## Decision
Employees have an `is_active` flag. "Removing" an employee sets it to `false`; rows are never deleted.

## Consequences
- **+** Salary history and past pay data are preserved.
- **+** Deactivation is reversible.
- **−** Every read must decide whether to include inactive employees. Defaults:
  - the directory hides them unless a filter is applied;
  - insights always exclude them.
- **−** Unique constraints still apply to inactive employees, so a former employee's email and employee code cannot be reused.
- Indexes lead with `is_active` because active-only filtering is on every insight query.
