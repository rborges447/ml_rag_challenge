from pathlib import Path
from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient


def test_upload_document_endpoint_accepts_pdf(test_client: TestClient, tmp_path: Path) -> None:
    """POST /documents aceita PDF e retorna 200 com message e total_chunks quando ingestão retorna sucesso."""
    pdf_path = tmp_path / "dummy.pdf"
    pdf_path.write_bytes(b"%PDF-1.4\n%EOF\n")

    with patch(
        "app.api.routes_documents.document_ingestion_use_case.run",
        new_callable=AsyncMock,
        return_value={"total_chunks": 5, "file_path": str(pdf_path)},
    ):
        with pdf_path.open("rb") as f:
            files = {"file": ("dummy.pdf", f, "application/pdf")}
            response = test_client.post("/documents", files=files)

    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "total_chunks" in data
    assert data["total_chunks"] == 5

