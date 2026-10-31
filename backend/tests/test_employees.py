import re
from typing import Any

import pytest
from fastapi.testclient import TestClient

EMPLOYEES = "/api/v1/employees"


def create(client: TestClient, **overrides: Any) -> dict[str, Any]:
    payload = {
        "full_name": "Asha Rao",
        "email": f"{overrides.get('full_name', 'asha').replace(' ', '.').lower()}@example.com",
        "job_title": "Software Engineer",
        "country_code": "IN",
        "salary_amount": "2000000.00",
        "salary_currency": "INR",
        **overrides,
    }
    response = client.post(EMPLOYEES, json=payload)
    assert response.status_code == 201, response.text
    return response.json()  # type: ignore[no-any-return]


@pytest.mark.parametrize(
    ("method", "path"),
    [
        ("get", EMPLOYEES),
        ("post", EMPLOYEES),
        ("get", f"{EMPLOYEES}/1"),
        ("patch", f"{EMPLOYEES}/1"),
        ("get", f"{EMPLOYEES}/1/salary-history"),
        ("get", "/api/v1/countries"),
        ("get", "/api/v1/currencies"),
    ],
)
def test_salary_data_requires_login(client: TestClient, method: str, path: str) -> None:
    assert client.request(method, path, json={}).status_code == 401


def test_create_generates_code_and_records_starting_salary(auth_client: TestClient) -> None:
    employee = create(auth_client)

    assert re.fullmatch(r"EMP-\d{6}", employee["employee_code"])
    assert employee["salary_usd"] == "21062.56"  # 2,000,000 INR at the seeded rate

    history = auth_client.get(f"{EMPLOYEES}/{employee['id']}/salary-history").json()
    assert [(h["old_amount"], h["new_amount"]) for h in history] == [(None, "2000000.00")]


def test_salary_change_is_recorded_and_currency_is_locked(auth_client: TestClient) -> None:
    employee = create(auth_client)
    url = f"{EMPLOYEES}/{employee['id']}"

    raised = auth_client.patch(url, json={"salary_amount": "2200000.00"})
    assert raised.status_code == 200

    rejected = auth_client.patch(url, json={"salary_amount": "1.00", "salary_currency": "USD"})
    assert rejected.status_code == 422
    assert auth_client.get(url).json()["salary_amount"] == "2200000.00"  # nothing applied

    history = auth_client.get(f"{url}/salary-history").json()
    assert [(h["old_amount"], h["new_amount"]) for h in history] == [
        ("2000000.00", "2200000.00"),
        (None, "2000000.00"),
    ]


def test_duplicate_email_is_rejected(auth_client: TestClient) -> None:
    create(auth_client, email="asha@example.com")

    response = auth_client.post(
        EMPLOYEES,
        json={
            "full_name": "Someone Else",
            "email": "ASHA@example.com",  # emails are case-insensitive
            "job_title": "Designer",
            "country_code": "US",
            "salary_amount": "90000.00",
            "salary_currency": "USD",
        },
    )

    assert response.status_code == 409


def test_status_filter_hides_inactive_by_default(auth_client: TestClient) -> None:
    active = create(auth_client, full_name="Still Here")
    gone = create(auth_client, full_name="Moved On")
    auth_client.patch(f"{EMPLOYEES}/{gone['id']}", json={"is_active": False})

    def ids(query: str) -> set[int]:
        return {e["id"] for e in auth_client.get(f"{EMPLOYEES}{query}").json()["items"]}

    assert ids("") == {active["id"]}
    assert ids("?status=inactive") == {gone["id"]}
    assert ids("?status=all") == {active["id"], gone["id"]}


def test_salary_sort_uses_usd_across_currencies(auth_client: TestClient) -> None:
    # Raw amounts would order GBP < USD < INR; in USD it is INR < GBP < USD.
    india = create(auth_client, full_name="In India")  # 2,000,000 INR ~ $21k
    uk = create(
        auth_client,
        full_name="In UK",
        country_code="GB",
        salary_amount="50000.00",
        salary_currency="GBP",
    )  # ~ $67k
    us = create(
        auth_client,
        full_name="In US",
        country_code="US",
        salary_amount="100000.00",
        salary_currency="USD",
    )

    items = auth_client.get(f"{EMPLOYEES}?sort=salary").json()["items"]

    assert [e["id"] for e in items] == [india["id"], uk["id"], us["id"]]


def test_pages_never_repeat_or_skip_employees_with_the_same_name(
    auth_client: TestClient,
) -> None:
    same_name = [
        create(auth_client, full_name="Alex Fischer", email=f"alex{i}@example.com")
        for i in range(3)
    ]
    # Updating a row moves it in physical storage, so without a tie-breaker the
    # database would be free to return the tied names in a different order.
    auth_client.patch(f"{EMPLOYEES}/{same_name[0]['id']}", json={"job_title": "Designer"})

    seen = []
    for page in (1, 2):
        response = auth_client.get(f"{EMPLOYEES}?sort=name&page_size=2&page={page}")
        seen += [e["id"] for e in response.json()["items"]]

    assert seen == sorted(e["id"] for e in same_name)
