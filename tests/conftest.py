from typing import Generator

import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


@pytest.fixture(scope="session")
def test_client() -> Generator[TestClient, None, None]:
    """Cliente de teste para a API FastAPI. Import do app é lazy para não carregar deps em testes que não usam a API."""
    from app.main import app  # noqa: E402

    with TestClient(app) as client:
        yield client

