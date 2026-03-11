from fastapi import APIRouter, File, HTTPException, UploadFile

from app.schemas.document import DocumentUploadResponse
from app.services.document_ingestion_service import DocumentIngestionService

router = APIRouter(tags=["documents"])

document_ingestion_service = DocumentIngestionService()


@router.post("/documents", response_model=DocumentUploadResponse)
async def upload_documents(
    file: UploadFile = File(..., description="Upload a PDF file")
) -> DocumentUploadResponse:
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail=f"Arquivo inválido: {file.filename}. Apenas PDFs são aceitos.",
        )

    result = await document_ingestion_service.process_uploaded_file(file)

    return DocumentUploadResponse(
        message="Document processed and indexed successfully",
        documents_indexed=1,
        total_chunks=result["total_chunks"],
    )