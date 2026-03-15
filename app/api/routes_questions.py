from fastapi import APIRouter, Query

from app.api.schemas import QuestionRequest, QuestionResponse
from app.core.dependencies import get_vector_store
from app.pipelines import QuestionPipeline

router = APIRouter(tags=["questions"])

_question_pipeline: QuestionPipeline | None = None


def _get_question_pipeline() -> QuestionPipeline:
    global _question_pipeline
    if _question_pipeline is None:
        _question_pipeline = QuestionPipeline(vector_store=get_vector_store())
    return _question_pipeline


@router.post("/question", response_model=QuestionResponse)
def ask_question(
    payload: QuestionRequest,
    top_k: int = Query(5, ge=1, le=50, description="Número máximo de chunks retornados após rerank"),
    initial_k: int | None = Query(None, ge=1, le=100, description="Candidatos buscados no Chroma antes do rerank (default: config)"),
    max_distance: float | None = Query(None, ge=0, description="Filtrar por distância L2 máxima (ChromaDB)"),
) -> QuestionResponse:
    pipeline = _get_question_pipeline()
    result = pipeline.run(
        question=payload.question,
        top_k=top_k,
        initial_k=initial_k,
        max_distance=max_distance,
    )
    return QuestionResponse(**result)
