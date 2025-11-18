from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_root_health():
    r = client.get("/")
    assert r.status_code == 200
    data = r.json()
    assert data.get("status") in {"healthy", "ok"}


def test_api_v1_health():
    r = client.get("/api/v1/health")
    assert r.status_code == 200
    data = r.json()
    assert data.get("status") == "ok"
