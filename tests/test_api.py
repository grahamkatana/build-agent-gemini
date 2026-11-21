from unittest.mock import patch
from fastapi.testclient import TestClient

from src.app import app

client = TestClient(app)


@patch("src.handlers.bus_chat_handler.get_gemini_response")
def test_chat_formatted_output(mock_gemini):
    mock_gemini.return_value = "The first weekday bus for **CENTURION** departs Potgieter Street at **05:30:00**."

    response = client.post(
        "/api/v1/chat",
        json={"query": "First weekday bus to Centurion?", "session_id": "sess-01"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "success"
    assert "05:30:00" in body["data"]["answer"]
    assert body["data"]["routes_mentioned"] == [
        {"route_code": "CENTURION", "name": None, "region": None}
    ]
    assert body["meta"]["session_id"] == "sess-01"
    assert isinstance(body["meta"]["latency_ms"], int)


@patch("src.handlers.bus_chat_handler.get_gemini_response")
def test_chat_rate_limit(mock_gemini):
    mock_gemini.return_value = "Mocked response"

    statuses = []
    for _ in range(17):
        res = client.post("/api/v1/chat", json={"query": "Bus to Brooklyn?"})
        statuses.append(res.status_code)

    assert 429 in statuses
