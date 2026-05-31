from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data


def test_metrics():
    response = client.get("/stores/STORE_001/metrics")
    assert response.status_code == 200
    data = response.json()
    assert "store_id" in data


def test_funnel():
    response = client.get("/stores/STORE_001/funnel")
    assert response.status_code == 200
    data = response.json()
    assert "visitors" in data


def test_sales():
    response = client.get("/stores/ST1008/sales")
    assert response.status_code == 200
    data = response.json()
    assert "revenue" in data
