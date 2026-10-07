import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


@pytest.mark.parametrize(
    "department,equipment_id,quantity,available,expected",
    [
        ("it", 1, 3, 3, True),
        ("general", 1, 3, 3, False),
        ("general", 1, 2, 3, True),
        ("it", 1, 4, 3, False),
        ("general", 1, 4, 3, False),
        ("it", 2, 1, 0, False),
        ("general", 2, 1, 0, False),
    ],
)
def test_department_policy(department, equipment_id, quantity, available, expected):
    response = client.get(
        f"/equipment/{equipment_id}/availability",
        params={"quantity": quantity, "department": department},
    )
    assert response.status_code == 200
    assert response.json() == {
        "equipment_id": equipment_id,
        "requested_quantity": quantity,
        "available_quantity": available,
        "can_allocate": expected,
    }


def test_omitted_department_keeps_previous_policy():
    response = client.get("/equipment/1/availability", params={"quantity": 3})
    assert response.status_code == 200
    assert response.json()["can_allocate"] is True


@pytest.mark.parametrize("department", ["sales", "IT", ""])
def test_unsupported_department_is_rejected(department):
    response = client.get(
        "/equipment/1/availability",
        params={"quantity": 1, "department": department},
    )
    assert response.status_code == 422


@pytest.mark.parametrize("quantity", [0, -1])
def test_invalid_quantity_is_rejected_with_department(quantity):
    response = client.get(
        "/equipment/1/availability",
        params={"quantity": quantity, "department": "general"},
    )
    assert response.status_code == 422


def test_unknown_equipment_returns_404_with_department():
    response = client.get(
        "/equipment/999/availability",
        params={"quantity": 1, "department": "it"},
    )
    assert response.status_code == 404


def test_availability_check_does_not_change_stock():
    before = client.get("/equipment").json()
    for department in ("it", "general"):
        client.get(
            "/equipment/1/availability",
            params={"quantity": 3, "department": department},
        )
    assert client.get("/equipment").json() == before
