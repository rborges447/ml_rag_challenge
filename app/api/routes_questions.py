from fastapi import APIRouter, Query

from app.schemas import QuestionRequest, QuestionResponse
from app.services import get_qa_service

router = APIRouter(tags=["questions"])

qa_service = get_qa_service()


@router.post("/question", response_model=QuestionResponse)
def ask_question(
    payload: QuestionRequest,
    top_k: int = Query(5, ge=1, le=50, description="Número máximo de chunks retornados após rerank"),
    initial_k: int | None = Query(None, ge=1, le=100, description="Candidatos buscados no Chroma antes do rerank (default: config)"),
    max_distance: float | None = Query(None, ge=0, description="Filtrar por distância L2 máxima (ChromaDB)"),
) -> QuestionResponse:
    result = qa_service.answer(
        question=payload.question,
        top_k=top_k,
        initial_k=initial_k,
        max_distance=max_distance,
    )
    return QuestionResponse(**result)
