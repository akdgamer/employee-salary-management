# Requirements

## Goal

Give ACME's HR manager a web application to manage salary data for ~10,000 employees across multiple countries, replacing spreadsheets, and to answer questions about how the organisation pays people.

## User and problem

- **Persona:** the HR manager, the single user of the system.
- **Problem:** salary data lives in spreadsheets. Editing is error-prone, there is no record of who changed what, and comparing pay across countries means converting currencies by hand.

## In scope

| Feature | Details | Why |
|---|---|---|
| Sign-in | Single HR manager account; every page and API call requires authentication | Salary data is sensitive |
| Employee directory | Paginated table; search by name, email or employee code; filter by country | Finding one person among 10,000 must be instant |
| Sorting | Sort by name, country or salary. Salary sorts by the USD-converted amount so different currencies rank correctly | Finding the highest and lowest paid is a core HR question |
| Manage employees | Create, edit and delete employees with validation (required fields, positive salary, unique email and employee code) | Replaces manual spreadsheet edits |
| Multi-currency salaries | Salary stored in the employee's local currency; table shows the native amount (e.g. ₹20,00,000) with its USD equivalent | Employees are contracted in local currency; USD gives a common basis for comparison |
| Salary history | Every salary change records old amount, new amount, currency, timestamp and who made it; viewable per employee | Salary is sensitive, so every change must be traceable |
| Pay insights (USD) | Min / max / average per country; average per job title within a country; one job title compared across countries; salary percentiles (p25, p50, p75, p90) per country; top-paying titles per country | Answers "how does the org pay people?" directly |
| Seed data | Deterministic script generating 10,000 realistic employees | Reproducible demo and test data |

## Assumptions

- Exchange rates are a **static snapshot** stored in the database with an "as of" date shown in the UI. Converted figures are indicative, not live.
- Each employee is paid in one currency.
- Money is stored with exact decimal precision, never floating point.

## Deliberately out of scope

| Excluded | Reason |
|---|---|
| Payments integration | This tool manages and analyses pay data. Moving money requires banking integration and per-country compliance, which is a different product |
| Excel / CSV import | Deferred to a later iteration to keep the first release focused on core features; the seed script supplies initial data |
| Display-currency selector | Deferred to a later iteration; all converted figures and insights use USD |
| Bonuses, equity and benefits | Base salary answers the core pay questions; variable pay and vesting would multiply the data model |
| Org hierarchy | None of the in-scope pay questions depend on reporting lines |

## Success criteria

- The HR manager can find, edit and audit any employee's salary in a few clicks.
- Every insight above loads quickly on the full 10,000-employee dataset.
- Core logic is covered by fast, deterministic automated tests.
