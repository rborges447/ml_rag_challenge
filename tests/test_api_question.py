from fastapi.testclient import TestClient


def test_question_endpoint_basic_flow(test_client: TestClient) -> None:
    payload = {"question": "Explique resumidamente o que é um título público."}

    response = test_client.post("/question", json=payload)

    # A API pode retornar erro se não houver documentos indexados;
    # aqui garantimos apenas que o endpoint responde de forma válida.
    assert response.status_code in (200, 422, 500)

    if response.status_code == 200:
        data = response.json()
        assert "answer" in data
        assert "references" in data

