from fastapi import APIRouter, Query

from app.schemas.question import QuestionRequest
from app.services.retrieval_service import RetrievalService

router = APIRouter(tags=["questions"])

retrieval_service = RetrievalService()


@router.post("/question")
def ask_question(
    payload: QuestionRequest,
    top_k: int = Query(8, ge=1, le=50, description="Número máximo de chunks retornados"),
    max_distance: float | None = Query(None, ge=0, description="Filtrar chunks com distância L2 maior que este valor (ChromaDB)"),
) -> dict:
    chunks = retrieval_service.retrieve(
        payload.question,
        top_k=top_k,
        max_distance=max_distance,
    )
    return {
        "question": payload.question,
        "retrieved_chunks": chunks,
    }
