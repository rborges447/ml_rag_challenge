from fastapi import APIRouter, Query

from app.schemas.question import QuestionRequest
from app.services.qa_service import get_qa_service

router = APIRouter(tags=["questions"])

qa_service = get_qa_service()


@router.post("/question")
def ask_question(
    payload: QuestionRequest,
    top_k: int = Query(5, ge=1, le=50, description="Número máximo de chunks retornados após rerank"),
    initial_k: int | None = Query(None, ge=1, le=100, description="Candidatos buscados no Chroma antes do rerank (default: config)"),
    max_distance: float | None = Query(None, ge=0, description="Filtrar por distância L2 máxima (ChromaDB)"),
) -> dict:
    chunks = qa_service.retrieve(
        payload.question,
        top_k=top_k,
        initial_k=initial_k,
        max_distance=max_distance,
    )
    return {
        "question": payload.question,
        "retrieved_chunks": chunks,
    }
