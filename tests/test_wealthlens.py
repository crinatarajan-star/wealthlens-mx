"""
WealthLens MX — test suite
Run: pytest tests/ -v
"""
import pytest
import json
import os
import tempfile

# Set env before importing app
os.environ["SECRET_KEY"] = "test-secret-key"
os.environ["GROQ_API_KEY"] = ""  # AI disabled in tests


@pytest.fixture
def app():
    """Create app with isolated test database."""
    import app as wl_app

    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    wl_app.DB_PATH = db_path
    wl_app.app.config["TESTING"] = True
    wl_app.app.config["WTF_CSRF_ENABLED"] = False
    wl_app.init_db()

    yield wl_app.app

    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def auth_client(client):
    """A client that's already registered and logged in."""
    client.post("/register", data={
        "name": "Test User",
        "email": "test@wealthlens.mx",
        "password": "TestPass123!"
    })
    client.post("/login", data={
        "email": "test@wealthlens.mx",
        "password": "TestPass123!"
    })
    return client


# ── Auth ──────────────────────────────────────────────────────────────────────

class TestAuth:
    def test_root_redirects_to_login(self, client):
        r = client.get("/")
        assert r.status_code == 302
        assert "/login" in r.headers["Location"]

    def test_login_page_loads(self, client):
        r = client.get("/login")
        assert r.status_code == 200

    def test_register_page_loads(self, client):
        r = client.get("/register")
        assert r.status_code == 200

    def test_register_and_login(self, client):
        r = client.post("/register", data={
            "name": "Ana García",
            "email": "ana@example.mx",
            "password": "SecurePass99!"
        }, follow_redirects=True)
        assert r.status_code == 200

        r = client.post("/login", data={
            "email": "ana@example.mx",
            "password": "SecurePass99!"
        }, follow_redirects=False)
        assert r.status_code == 302
        assert "/dashboard" in r.headers["Location"]

    def test_login_wrong_password(self, client):
        client.post("/register", data={
            "name": "Bob",
            "email": "bob@example.mx",
            "password": "CorrectPassword1"
        })
        r = client.post("/login", data={
            "email": "bob@example.mx",
            "password": "WrongPassword!"
        }, follow_redirects=True)
        assert r.status_code == 200  # stays on login page

    def test_duplicate_email_rejected(self, client):
        data = {"name": "User", "email": "dup@example.mx", "password": "Pass123!"}
        client.post("/register", data=data)
        r = client.post("/register", data=data, follow_redirects=True)
        assert r.status_code == 200  # redirected back with flash

    def test_protected_routes_require_login(self, client):
        for route in ["/dashboard", "/api/status", "/api/wealth/summary"]:
            r = client.get(route)
            assert r.status_code in (302, 401), f"{route} should require login"

    def test_logout_clears_session(self, auth_client):
        r = auth_client.get("/logout", follow_redirects=False)
        assert r.status_code == 302
        r = auth_client.get("/dashboard")
        assert r.status_code == 302  # redirected away — session cleared


# ── API endpoints ─────────────────────────────────────────────────────────────

class TestApiStatus:
    def test_status_returns_ok(self, auth_client):
        r = auth_client.get("/api/status")
        assert r.status_code == 200
        data = json.loads(r.data)
        assert data["ok"] is True
        assert "version" in data
        assert "features" in data

    def test_status_reports_ai_unconfigured(self, auth_client):
        r = auth_client.get("/api/status")
        data = json.loads(r.data)
        assert data["ai_configured"] is False  # no GROQ_API_KEY in test env


class TestWealthSummary:
    def test_wealth_summary_structure(self, auth_client):
        r = auth_client.get("/api/wealth/summary")
        assert r.status_code == 200
        data = json.loads(r.data)
        assert "wealth" in data
        assert "goals" in data
        assert "recent_30_days" in data

    def test_wealth_summary_defaults_zero(self, auth_client):
        r = auth_client.get("/api/wealth/summary")
        data = json.loads(r.data)
        assert data["wealth"]["total_assets_mxn"] == 0
        assert data["wealth"]["asset_count"] == 0

    def test_wealth_summary_keys(self, auth_client):
        r = auth_client.get("/api/wealth/summary")
        data = json.loads(r.data)
        assert "total_assets_mxn" in data["wealth"]
        assert "total_goals" in data["goals"]
        assert "income_mxn" in data["recent_30_days"]
        assert "expenses_mxn" in data["recent_30_days"]


class TestMarketEndpoints:
    def test_deposits_endpoint(self, auth_client):
        r = auth_client.get("/api/market/deposits")
        assert r.status_code == 200
        data = json.loads(r.data)
        assert "rates" in data
        assert len(data["rates"]) > 0
        first = data["rates"][0]
        assert "bank" in first
        assert "rate" in first

    def test_deposits_sorted_by_rate(self, auth_client):
        r = auth_client.get("/api/market/deposits")
        data = json.loads(r.data)
        rates = [d["rate"] for d in data["rates"]]
        assert rates == sorted(rates, reverse=True), "Rates should be sorted highest first"

    def test_crypto_endpoint_returns_200(self, auth_client):
        # CoinGecko may fail in CI — just assert we don't crash
        r = auth_client.get("/api/market/crypto?ids=bitcoin")
        assert r.status_code == 200

    def test_stocks_endpoint_returns_200(self, auth_client):
        r = auth_client.get("/api/market/stocks?symbols=SPY")
        assert r.status_code == 200


class TestChatApi:
    def test_chat_requires_question(self, auth_client):
        r = auth_client.post("/api/chat",
                             data=json.dumps({}),
                             content_type="application/json")
        assert r.status_code == 400
        data = json.loads(r.data)
        assert data["ok"] is False

    def test_chat_demo_mode(self, auth_client):
        """Without GROQ_API_KEY, chat should return demo response."""
        r = auth_client.post("/api/chat",
                             data=json.dumps({"question": "How can I save more money?"}),
                             content_type="application/json")
        assert r.status_code == 200
        data = json.loads(r.data)
        assert data["ok"] is True
        assert "answer" in data
        assert data["demo"] is True

    def test_chat_history_empty_at_start(self, auth_client):
        r = auth_client.get("/api/chat/history")
        assert r.status_code == 200
        data = json.loads(r.data)
        assert data["ok"] is True
        assert isinstance(data["history"], list)

    def test_chat_saves_to_history(self, auth_client):
        auth_client.post("/api/chat",
                         data=json.dumps({"question": "What is a CEDE?"}),
                         content_type="application/json")
        r = auth_client.get("/api/chat/history")
        data = json.loads(r.data)
        assert len(data["history"]) >= 1
        assert data["history"][0]["question"] == "What is a CEDE?"


# ── Utility / helpers ─────────────────────────────────────────────────────────

class TestHelpers:
    def test_dashboard_loads(self, auth_client):
        r = auth_client.get("/dashboard")
        assert r.status_code == 200

    def test_ai_dashboard_demo_mode(self, auth_client):
        """AI dashboard returns demo payload when key is missing."""
        r = auth_client.post("/api/ai/dashboard",
                             data=json.dumps({}),
                             content_type="application/json")
        assert r.status_code == 200
        data = json.loads(r.data)
        assert data["ok"] is True
        assert data["demo"] is True
        dash = data["dashboard"]
        assert "health_score" in dash
        assert "kpis" in dash
        assert "recommendations" in dash
