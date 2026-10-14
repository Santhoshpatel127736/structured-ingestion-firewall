
from unittest.mock import patch
from fastapi.testclient import TestClient

from main import app
from structured_output import SupportTicket, Intent, RiskProfile

client = TestClient(app)


def test_successful_ingestion():
    fake_ticket = SupportTicket(
        intent=Intent.BILLING_DISPUTE,
        risk_profile=RiskProfile.HIGH,
        priority=5,
        summary="Customer was charged twice and requests a refund.",
    )

    with patch("main.classify_message", return_value=fake_ticket):
        response = client.post(
            "/ingest",
            json={
                "text": "I was charged twice for my order and need a refund."
            },
        )

    assert response.status_code == 200

    data = response.json()
    assert data["intent"] == "billing_dispute"
    assert data["risk_profile"] == "high"
    assert data["priority"] == 5
    assert data["token_metadata"]["estimated_input_tokens"] > 0


def test_llm_failure_returns_502():
    with patch("main.classify_message", side_effect=RuntimeError("Simulated failure")):
        response = client.post(
            "/ingest",
            json={"text": "Please help me access my account."},
        )

    assert response.status_code == 502
    assert response.json()["detail"] == "LLM processing failed. Please retry later."
