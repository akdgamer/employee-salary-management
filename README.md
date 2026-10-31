# Salary Management

Web-based salary management for an HR manager overseeing ~10,000 employees across multiple countries. It replaces spreadsheet-based salary tracking and answers questions about how the organisation pays people.

> **Status:** work in progress. Documentation and implementation are added incrementally; see the commit history for how the solution evolved.

## Stack and rationale

| Layer | Choice | Why | Trade-off |
|---|---|---|---|
| Database | **PostgreSQL 16** | `percentile_cont` for salary distribution percentiles; `COPY` for fast bulk seeding; exact `NUMERIC` type for money; `CITEXT` for case-insensitive unique emails; available as a managed service | Needs a database server (Docker locally) where SQLite would need no setup |
| API | **FastAPI** (Python 3.11) | Pydantic validation at the API boundary; OpenAPI docs generated automatically; little boilerplate for a CRUD + analytics API | No built-in admin or auth; both are implemented by hand |
| Data access | **SQLAlchemy 2 + Alembic** | Composable queries for filters and aggregates; versioned, reviewable schema migrations | More setup than a lightweight query layer |
| UI | **React + Vite + TypeScript** | An authenticated internal dashboard gains nothing from server rendering or SEO, so a static single-page app is simpler to build and deploy than Next.js; TypeScript catches errors at compile time | No server-side rendering (not needed for an internal tool) |
| Components | **MUI + MUI X DataGrid** | DataGrid supports server-side pagination for 10k rows; mature, accessible form and dialog components; consistent look with little custom CSS | Larger bundle; the free DataGrid tier caps page size and omits some features |
| Server state | **TanStack Query** | Caching per query key, loading/error states, and automatic refetch after edits via query invalidation | One more dependency |
| Forms | **react-hook-form** | Form state and validation with minimal re-renders | One more dependency |
| Routing | **React Router** | Client-side routes for login, employees and insights, with protected routes | — |
| Charts | **Recharts** | Declarative React charts for salary distributions | Less flexible than lower-level charting libraries |

## Documentation

Requirements, design notes, architecture diagrams, trade-offs and performance notes will be linked here as they are added.
