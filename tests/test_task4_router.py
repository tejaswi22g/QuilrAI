from fastapi.testclient import TestClient

from task4_model_router.app import app


def test_primary_model_success():
    with TestClient(app) as client:
        response = client.post(
            "/generate",
            headers={"X-Tenant-ID": "router-success"},
            json={
                "prompt": "Hello AI",
                "estimated_tokens": 100,
                "primary_behavior": "success",
            },
        )

    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "success"
    assert data["fallback_used"] is False
    assert data["data"]["model"] == "primary-model"


def test_fallback_on_rate_limit():
    with TestClient(app) as client:
        response = client.post(
            "/generate",
            headers={"X-Tenant-ID": "router-rate-limit"},
            json={
                "prompt": "Hello AI",
                "estimated_tokens": 100,
                "primary_behavior": "rate_limit",
            },
        )

    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "success"
    assert data["fallback_used"] is True
    assert data["fallback_reason"] == "primary_rate_limited"
    assert data["data"]["model"] == "secondary-model"


def test_fallback_on_primary_timeout():
    with TestClient(app) as client:
        response = client.post(
            "/generate",
            headers={"X-Tenant-ID": "router-timeout"},
            json={
                "prompt": "Hello AI",
                "estimated_tokens": 100,
                "primary_behavior": "timeout",
            },
        )

    assert response.status_code == 200

    data = response.json()
    assert data["fallback_used"] is True
    assert data["fallback_reason"] == "primary_timeout"
    assert data["data"]["model"] == "secondary-model"


def test_token_rate_limit():
    with TestClient(app) as client:
        headers = {"X-Tenant-ID": "router-limit"}

        first = client.post(
            "/generate",
            headers=headers,
            json={
                "prompt": "First request",
                "estimated_tokens": 50000,
            },
        )

        second = client.post(
            "/generate",
            headers=headers,
            json={
                "prompt": "Second request",
                "estimated_tokens": 1,
            },
        )

    assert first.status_code == 200
    assert second.status_code == 429
    assert second.json()["detail"]["error"] == "Token rate limit exceeded"


def test_missing_tenant_id():
    with TestClient(app) as client:
        response = client.post(
            "/generate",
            json={
                "prompt": "Hello AI",
                "estimated_tokens": 100,
            },
        )

    assert response.status_code == 400
    assert response.json()["detail"] == "Tenant ID is required"