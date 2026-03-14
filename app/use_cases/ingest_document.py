"""
Use case: ingestão de documento (upload PDF → salvar → pipeline de ingestão).
"""
import os
import uuid

from fastapi import UploadFile

from app.core.config import settings
from app.services.pipelines import IngestionPipeline


class DocumentIngestionUseCase:
    """Recebe o arquivo PDF, salva em disco e executa o pipeline de ingestão."""

    def __init__(self, ingestion_pipeline: IngestionPipeline | None = None) -> None:
        self._pipeline = ingestion_pipeline or IngestionPipeline()
        self._upload_dir = settings.upload_dir

    async def run(self, file: UploadFile) -> dict:
        """
        Salva o PDF e executa o pipeline de ingestão.
        Retorna {"file_path": str, "total_chunks": int}.
        """
        os.makedirs(self._upload_dir, exist_ok=True)
        file_id = str(uuid.uuid4())
        file_path = os.path.join(self._upload_dir, f"{file_id}.pdf")

        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)

        source_name = file.filename or os.path.basename(file_path)
        result = self._pipeline.run(file_path=file_path, source_name=source_name)
        result["file_path"] = file_path
        return result
