import httpx

from fastapi.testclient import TestClient

import jarvis_noc.main as main
from jarvis_noc.main import app

client = TestClient(app)


def test_health_is_public():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_chat_requires_authentication(monkeypatch):
    monkeypatch.setenv("JARVIS_API_KEY", "test-key")
    response = client.post("/v1/chat/stream", json={"message": "hola"})
    assert response.status_code == 401


def test_chat_requires_configured_provider(monkeypatch):
    monkeypatch.setenv("JARVIS_API_KEY", "test-key")
    monkeypatch.delenv("JARVIS_MODEL_BASE_URL", raising=False)
    response = client.post(
        "/v1/chat/stream",
        headers={"Authorization": "Bearer test-key"},
        json={"message": "hola"},
    )
    assert response.status_code == 503


def test_voice_requires_authentication(monkeypatch):
    monkeypatch.setenv("JARVIS_API_KEY", "test-key")
    response = client.post("/v1/voice/speak", json={"text": "hola"})
    assert response.status_code == 401


def test_chat_streams_provider_tokens(monkeypatch):
    monkeypatch.setenv("JARVIS_API_KEY", "test-key")
    monkeypatch.setenv("JARVIS_MODEL_BASE_URL", "http://model.test/v1")
    monkeypatch.setenv("JARVIS_MODEL_API_KEY", "provider-key")
    monkeypatch.setenv("JARVIS_MODEL_NAME", "test-model")

    def handler(request):
        assert request.url.path == "/v1/chat/completions"
        assert request.headers["authorization"] == "Bearer provider-key"
        assert b"test-model" in request.content
        return httpx.Response(200, text='data: {"choices":[{"delta":{"content":"Hola"}}]}\n\ndata: [DONE]\n\n')

    transport = httpx.MockTransport(handler)
    original_client = httpx.AsyncClient
    monkeypatch.setattr(main.httpx, "AsyncClient", lambda **kwargs: original_client(transport=transport, **kwargs))
    response = client.post(
        "/v1/chat/stream",
        headers={"Authorization": "Bearer test-key"},
        json={"message": "hola"},
    )
    assert response.status_code == 200
    assert '"delta": "Hola"' in response.text
    assert "data: [DONE]" in response.text
