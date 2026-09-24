import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Tests use SQLite so CI does not need Neon credentials.
os.environ.setdefault("DATABASE_URL", "sqlite:///./test_employee.db")

from app.database import Base, get_db  # noqa: E402
from app.main import app  # noqa: E402

test_engine = create_engine(
    "sqlite:///./test_employee.db",
    connect_args={"check_same_thread": False},
)
TestSessionLocal = sessionmaker(bind=test_engine, autoflush=False, autocommit=False)


def override_get_db():
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_database():
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
    yield


def test_create_and_get_employee():
    payload = {
        "name": "Vikram",
        "email": "vikram@example.com",
        "department": "Engineering",
    }
    create_response = client.post("/employees/", json=payload)
    assert create_response.status_code == 201
    employee = create_response.json()
    assert employee["name"] == "Vikram"
    assert employee["email"] == "vikram@example.com"

    get_response = client.get(f"/employees/{employee['id']}")
    assert get_response.status_code == 200
    assert get_response.json()["email"] == "vikram@example.com"


def test_list_employees():
    client.post(
        "/employees/",
        json={"name": "Amit", "email": "amit@example.com", "department": "Engineering"},
    )
    client.post(
        "/employees/",
        json={"name": "Neha", "email": "neha@example.com", "department": "HR"},
    )
    response = client.get("/employees/")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_update_employee():
    create_response = client.post(
        "/employees/",
        json={"name": "Rahul", "email": "rahul@example.com", "department": "HR"},
    )
    employee_id = create_response.json()["id"]
    response = client.put(
        f"/employees/{employee_id}",
        json={"department": "Finance"},
    )
    assert response.status_code == 200
    assert response.json()["department"] == "Finance"


def test_duplicate_email_returns_conflict():
    payload = {
        "name": "Amit",
        "email": "amit@example.com",
        "department": "Engineering",
    }
    assert client.post("/employees/", json=payload).status_code == 201
    response = client.post("/employees/", json=payload)
    assert response.status_code == 409


def test_delete_employee():
    response = client.post(
        "/employees/",
        json={"name": "Neha", "email": "neha@example.com", "department": "Operations"},
    )
    employee_id = response.json()["id"]
    delete_response = client.delete(f"/employees/{employee_id}")
    assert delete_response.status_code == 204
    get_response = client.get(f"/employees/{employee_id}")
    assert get_response.status_code == 404


def test_get_employee_not_found():
    response = client.get("/employees/99999")
    assert response.status_code == 404


def test_update_employee_not_found():
    response = client.put("/employees/99999", json={"name": "Nobody"})
    assert response.status_code == 404


def test_delete_employee_not_found():
    response = client.delete("/employees/99999")
    assert response.status_code == 404


def test_create_employee_validation_error():
    # Missing required fields / invalid email
    response = client.post(
        "/employees/",
        json={"name": "X", "email": "not-an-email", "department": "Eng"},
    )
    assert response.status_code == 422


def test_create_employee_short_name():
    response = client.post(
        "/employees/",
        json={"name": "A", "email": "a@example.com", "department": "Eng"},
    )
    assert response.status_code == 422
