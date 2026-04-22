from __future__ import annotations


def test_health_endpoints_return_ready(client):
    live = client.get("/health/live")
    ready = client.get("/health/ready")

    assert live.status_code == 200
    assert ready.status_code == 200
