"""Kayıt ve giriş endpoint testleri."""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.models.base import get_db


@pytest.fixture()
def client(db):
    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

def test_register_success(client):
    response = client.post(
        "/auth/register",
        json={"email": "newuser@gmail.com", "password": "TestPass1!"},
    )
    assert response.status_code == 201
    body = response.json()
    assert "access_token" in body
    assert "refresh_token" in body

def test_register_duplicate_email_returns_400(client):
    payload = {"email": "dup@gmail.com", "password": "TestPass1!"}
    first = client.post("/auth/register", json=payload)
    second = client.post("/auth/register", json=payload)

    assert first.status_code == 201
    assert second.status_code == 400
    assert "bu e-posta" in second.json()["detail"].lower()

def test_login_after_register(client):
    payload = {"email": "loginflow@gmail.com", "password": "TestPass1!"}
    register = client.post("/auth/register", json=payload)
    login = client.post("/auth/login", json=payload)

    assert register.status_code == 201
    assert login.status_code == 200
    assert "access_token" in login.json()
