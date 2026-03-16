import os
import uuid

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.api.schemas import DocumentUploadResponse
from app.core.config import settings
from app.core.dependencies import get_document_processing_service
from app.core.logging import get_logger
from app.pipelines import IngestionPipeline

logger = get_logger(__name__)
router = APIRouter(tags=["documents"])

_ingestion_pipeline: IngestionPipeline | None = None


def _get_ingestion_pipeline() -> IngestionPipeline:
    global _ingestion_pipeline
    if _ingestion_pipeline is None:
        _ingestion_pipeline = IngestionPipeline(
            ingestion_service=get_document_processing_service(),
        )
    return _ingestion_pipeline


@router.post("/documents", response_model=DocumentUploadResponse)
async def upload_documents(
    file: UploadFile = File(..., description="Upload a PDF file")
) -> DocumentUploadResponse:
    request_id = str(uuid.uuid4())
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail=f"Arquivo inválido: {file.filename}. Apenas PDFs são aceitos.",
        )

    logger.info(
        "request_id=%s | upload recebido filename=%s",
        request_id,
        file.filename or "(sem nome)",
    )
    try:
        os.makedirs(settings.upload_dir, exist_ok=True)
        file_id = str(uuid.uuid4())
        file_path = os.path.join(settings.upload_dir, f"{file_id}.pdf")
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)
        source_name = file.filename or os.path.basename(file_path)

        logger.info(
            "request_id=%s | início processamento source_name=%s",
            request_id,
            source_name,
        )
        pipeline = _get_ingestion_pipeline()
        result = pipeline.run(
            file_path=file_path,
            source_name=source_name,
            request_id=request_id,
        )

        logger.info(
            "request_id=%s | sucesso total_chunks=%s documents_indexed=1",
            request_id,
            result["total_chunks"],
        )
        return DocumentUploadResponse(
            message="Document processed and indexed successfully",
            documents_indexed=1,
            total_chunks=result["total_chunks"],
        )
    except Exception:
        logger.exception("request_id=%s | falha no upload/processamento", request_id)
        raise
