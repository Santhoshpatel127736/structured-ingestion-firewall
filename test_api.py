
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {"status": "running"}


def test_rejects_short_message():
    response = client.post(
        "/ingest",
        json={"text": "Hi"},
    )

    assert response.status_code == 422


def test_rejects_empty_message():
    response = client.post(
        "/ingest",
        json={"text": ""},
    )

    assert response.status_code == 422
