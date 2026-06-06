"""
WealthLens MX — test suite
Placed in repo ROOT (same level as app.py) so CI can find it without a templates/ folder.
Run: pytest test_app.py -v
"""
import pytest
import json
import os
import tempfile

os.environ.setdefault("SECRET_KEY", "test-secret-key")
os.environ.setdefault("GROQ_API_KEY", "")


@pytest.fixture(scope="session")
def app():
    import app as wl
    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    wl.DB_PATH = db_path
    wl.app.config["TESTING"] = True
    wl.init_db()
    yield wl.app
    os.close(db_fd)
    try:
        os.unlink(db_path)
    except Exception:
        pass


@pytest.fixture(scope="session")
def client(app):
    return app.test_client()


@pytest.fixture(scope="session")
def auth_client(client):
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
    def test_root_redirects(self, client):
        r = client.get("/")
        assert r.status_code == 302

    def test_login_page_loads(self, client):
        r = client.get("/login")
        assert r.status_code == 200

    def test_register_page_loads(self, client):
        r = client.get("/register")
        assert r.status_code == 200

    def test_register_and_login(self, client):
        client.post("/register", data={
            "name": "Ana Test",
            "email": "ana@test.mx",
            "password": "Pass99!"
        })
        r = client.post("/login", data={
            "email": "ana@test.mx",
            "password": "Pass99!"
        })
        assert r.status_code in (200, 302)

    def test_wrong_password_stays_on_login(self, client):
        r = client.post("/login", data={
            "email": "nobody@test.mx",
            "password": "wrong"
        }, follow_redirects=True)
        assert r.status_code == 200

    def test_protected_dashboard_requires_login(self, client):
        fresh = client.application.test_client()
        r = fresh.get("/dashboard")
        assert r.status_code == 302

    def test_logout_clears_session(self, auth_client):
        r = auth_client.get("/logout")
        assert r.status_code in (200, 302)


# ── API ───────────────────────────────────────────────────────────────────────

class TestApiStatus:
    def test_status_ok(self, auth_client):
        r = auth_client.get("/api/status")
        assert r.status_code == 200
        data = json.loads(r.data)
        assert data["ok"] is True

    def test_status_has_version(self, auth_client):
        r = auth_client.get("/api/status")
        data = json.loads(r.data)
        assert "version" in data

    def test_status_has_features(self, auth_client):
        r = auth_client.get("/api/status")
        data = json.loads(r.data)
        assert isinstance(data.get("features"), list)

    def test_ai_not_configured_without_key(self, auth_client):
        r = auth_client.get("/api/status")
        data = json.loads(r.data)
        assert data["ai_configured"] is False


class TestWealthSummary:
    def test_summary_returns_200(self, auth_client):
        r = auth_client.get("/api/wealth/summary")
        assert r.status_code == 200

    def test_summary_has_wealth_key(self, auth_client):
        r = auth_client.get("/api/wealth/summary")
        data = json.loads(r.data)
        assert "wealth" in data

    def test_summary_has_goals_key(self, auth_client):
        r = auth_client.get("/api/wealth/summary")
        data = json.loads(r.data)
        assert "goals" in data

    def test_summary_has_recent_key(self, auth_client):
        r = auth_client.get("/api/wealth/summary")
        data = json.loads(r.data)
        assert "recent_30_days" in data

    def test_new_user_has_zero_assets(self, auth_client):
        r = auth_client.get("/api/wealth/summary")
        data = json.loads(r.data)
        assert data["wealth"]["total_assets_mxn"] == 0


class TestMarketEndpoints:
    def test_deposits_returns_200(self, auth_client):
        r = auth_client.get("/api/market/deposits")
        assert r.status_code == 200

    def test_deposits_has_rates(self, auth_client):
        r = auth_client.get("/api/market/deposits")
        data = json.loads(r.data)
        assert "rates" in data
        assert len(data["rates"]) > 0

    def test_deposits_sorted_descending(self, auth_client):
        r = auth_client.get("/api/market/deposits")
        data = json.loads(r.data)
        rates = [d["rate"] for d in data["rates"]]
        assert rates == sorted(rates, reverse=True)

    def test_crypto_endpoint_doesnt_crash(self, auth_client):
        r = auth_client.get("/api/market/crypto?ids=bitcoin")
        assert r.status_code == 200

    def test_stocks_endpoint_doesnt_crash(self, auth_client):
        r = auth_client.get("/api/market/stocks?symbols=SPY")
        assert r.status_code == 200


class TestChatApi:
    def test_chat_empty_question_is_400(self, auth_client):
        r = auth_client.post("/api/chat",
                             data=json.dumps({}),
                             content_type="application/json")
        assert r.status_code == 400

    def test_chat_returns_demo_without_key(self, auth_client):
        r = auth_client.post("/api/chat",
                             data=json.dumps({"question": "How to save more?"}),
                             content_type="application/json")
        assert r.status_code == 200
        data = json.loads(r.data)
        assert data["ok"] is True
        assert "answer" in data
        assert data.get("demo") is True

    def test_chat_history_starts_empty(self, client):
        fresh = client.application.test_client()
        fresh.post("/register", data={"name":"H","email":"h@h.mx","password":"Pass1!"})
        fresh.post("/login", data={"email":"h@h.mx","password":"Pass1!"})
        r = fresh.get("/api/chat/history")
        data = json.loads(r.data)
        assert data["ok"] is True
        assert isinstance(data["history"], list)

    def test_chat_saves_to_history(self, auth_client):
        auth_client.post("/api/chat",
                         data=json.dumps({"question": "What is a CEDE?"}),
                         content_type="application/json")
        r = auth_client.get("/api/chat/history")
        data = json.loads(r.data)
        questions = [h["question"] for h in data["history"]]
        assert "What is a CEDE?" in questions


class TestAiDashboard:
    def test_ai_dashboard_demo_mode(self, auth_client):
        r = auth_client.post("/api/ai/dashboard",
                             data=json.dumps({}),
                             content_type="application/json")
        assert r.status_code == 200
        data = json.loads(r.data)
        assert data["ok"] is True
        assert data.get("demo") is True

    def test_ai_dashboard_has_health_score(self, auth_client):
        r = auth_client.post("/api/ai/dashboard",
                             data=json.dumps({}),
                             content_type="application/json")
        data = json.loads(r.data)
        assert "health_score" in data["dashboard"]

    def test_ai_dashboard_has_kpis(self, auth_client):
        r = auth_client.post("/api/ai/dashboard",
                             data=json.dumps({}),
                             content_type="application/json")
        data = json.loads(r.data)
        assert isinstance(data["dashboard"].get("kpis"), list)
