from fastapi.testclient import TestClient
from main import app
import os


client = TestClient(app)


def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("status") == "healthy"


def test_session_new():
    resp = client.post("/session/new", json={"user_id": "dev", "project": "demo"})
    assert resp.status_code == 200
    data = resp.json()
    assert "session_id" in data
    assert "token" in data


def test_auth_login_and_validate():
    login = client.post("/auth/login", json={"user_id": "tester"})
    assert login.status_code == 200
    token = login.json().get("token")
    assert token
    validate = client.post("/auth/validate", json={"token": token})
    assert validate.status_code == 200
    assert validate.json().get("valid") is True


def test_execute_code_placeholder():
    # Works even if ADK executors are unavailable; contract should return a JSON body
    resp = client.post("/execute", json={"code": "print(1+1)"})
    assert resp.status_code == 200
    body = resp.json()
    assert "status" in body
def test_orchestrate_with_adk_flag_enabled():
    # Enabling the flag should not break the endpoint even if ADK is missing
    prev = os.environ.get("ADK_ENABLED")
    os.environ["ADK_ENABLED"] = "true"
    try:
        resp = client.post("/orchestrate", json={"message": "hello"})
        assert resp.status_code == 200
        body = resp.json()
        assert "status" in body
    finally:
        if prev is None:
            del os.environ["ADK_ENABLED"]
        else:
            os.environ["ADK_ENABLED"] = prev


def test_security_callback_blocks_dangerous_input():
    resp = client.post("/orchestrate", json={"message": "please rm -rf /"})
    assert resp.status_code == 200
    data = resp.json()
    # Should be blocked by before_model_callback
    assert data.get("blocked") is True


