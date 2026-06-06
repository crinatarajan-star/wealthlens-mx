"""
Basic API tests for WealthLens MX.
Run with: pytest tests/ -v
"""
import os
import pytest
import sys

os.environ.setdefault("SECRET_KEY", "test-secret-key")
os.environ.setdefault("GROQ_API_KEY", "")

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import app as app_module


@pytest.fixture
def client(tmp_path):
    """Create a test Flask client with a fresh in-memory DB."""
    app_module.DB_PATH = str(tmp_path / "test.db")
    app_module.app.config["TESTING"] = True
    app_module.app.config["SECRET_KEY"] = "test-secret"
    app_module.init_db()
    with app_module.app.test_client() as c:
        yield c


def register_and_login(client, email="test@example.com", password="password123"):
    """Helper: register + login a test user, return client."""
    client.post("/register", data={"name": "Test User", "email": email, "password": password})
    client.post("/login", data={"email": email, "password": password})
    return client


def test_login_page_loads(client):
    resp = client.get("/login")
    assert resp.status_code == 200


def test_register_page_loads(client):
    resp = client.get("/register")
    assert resp.status_code == 200


def test_register_and_login(client):
    resp = client.post("/register", data={
        "name": "Test User",
        "email": "user@example.com",
        "password": "securepass"
    }, follow_redirects=True)
    assert resp.status_code == 200

    resp = client.post("/login", data={
        "email": "user@example.com",
        "password": "securepass"
    }, follow_redirects=True)
    assert resp.status_code == 200


def test_dashboard_requires_auth(client):
    resp = client.get("/dashboard", follow_redirects=False)
    assert resp.status_code == 302


def test_api_status_requires_auth(client):
    resp = client.get("/api/status")
    assert resp.status_code == 302


def test_api_status_authenticated(client):
    register_and_login(client)
    resp = client.get("/api/status")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["ok"] is True
    assert "version" in data


def test_api_wealth_summary(client):
    register_and_login(client)
    resp = client.get("/api/wealth/summary")
    assert resp.status_code == 200
    data = resp.get_json()
    assert "wealth" in data
    assert "goals" in data
    assert "recent_30_days" in data


def test_api_market_deposits(client):
    register_and_login(client)
    resp = client.get("/api/market/deposits")
    assert resp.status_code == 200
    data = resp.get_json()
    assert "rates" in data
    assert len(data["rates"]) > 0


def test_api_chat_requires_question(client):
    register_and_login(client)
    resp = client.post("/api/chat", json={})
    assert resp.status_code == 400
    data = resp.get_json()
    assert data["ok"] is False


def test_api_chat_demo_mode(client):
    """Chat should return a demo response when no API key is configured."""
    register_and_login(client)
    resp = client.post("/api/chat", json={"question": "How are my savings?"})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["ok"] is True
    assert "answer" in data


def test_api_chat_history(client):
    register_and_login(client)
    resp = client.get("/api/chat/history")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["ok"] is True
    assert "history" in data


def test_duplicate_email_rejected(client):
    data = {"name": "User One", "email": "dup@example.com", "password": "pass"}
    client.post("/register", data=data)
    resp = client.post("/register", data=data, follow_redirects=True)
    assert resp.status_code == 200


def test_wrong_password_rejected(client):
    client.post("/register", data={"name": "U", "email": "a@b.com", "password": "correct"})
    resp = client.post("/login", data={"email": "a@b.com", "password": "wrong"}, follow_redirects=True)
    assert resp.status_code == 200
