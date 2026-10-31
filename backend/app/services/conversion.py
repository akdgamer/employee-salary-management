"""USD conversion in SQL (decision 0003), shared by listing and insights.

Queries using ``SALARY_USD`` must join currencies: ``.join(Currency, CURRENCY_JOIN)``.
"""

from app.models import Currency, Employee

CURRENCY_JOIN = Currency.code == Employee.salary_currency

SALARY_USD = Employee.salary_amount * Currency.rate_to_usd
"""Unrounded salary in USD; round only for display so aggregates stay exact."""
