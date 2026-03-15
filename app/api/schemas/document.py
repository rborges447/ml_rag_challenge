from pydantic import BaseModel


class DocumentUploadResponse(BaseModel):
    message: str
    documents_indexed: int
    total_chunks: int
