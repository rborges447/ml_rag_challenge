from fastapi.testclient import TestClient


def test_health_endpoint_ok(test_client: TestClient) -> None:
    response = test_client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert data.get("status") in {"ok", "healthy", "UP"}

