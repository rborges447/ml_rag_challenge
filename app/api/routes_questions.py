import uuid

from fastapi import APIRouter, Query

from app.api.schemas import QuestionRequest, QuestionResponse
from app.core.dependencies import get_question_pipeline
from app.core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter(tags=["questions"])


def _truncate(s: str, max_len: int = 80) -> str:
    if len(s) <= max_len:
        return s
    return s[:max_len] + "..."


@router.post("/question", response_model=QuestionResponse)
def ask_question(
    payload: QuestionRequest,
    top_k: int = Query(5, ge=1, le=50, description="Número máximo de chunks retornados após rerank"),
    initial_k: int | None = Query(None, ge=1, le=100, description="Candidatos buscados no Chroma antes do rerank (default: config)"),
    max_distance: float | None = Query(None, ge=0, description="Filtrar por distância L2 máxima (ChromaDB)"),
) -> QuestionResponse:
    request_id = str(uuid.uuid4())
    question = payload.question
    logger.info(
        "request_id=%s | pergunta recebida len=%s preview=%s",
        request_id,
        len(question),
        _truncate(question),
    )
    try:
        logger.info("request_id=%s | início processamento", request_id)
        pipeline = get_question_pipeline()
        result = pipeline.run(
            question=question,
            top_k=top_k,
            initial_k=initial_k,
            max_distance=max_distance,
            request_id=request_id,
        )
        refs_count = len(result.get("references") or [])
        chunks_count = len(result.get("retrieved_chunks") or [])
        logger.info(
            "request_id=%s | sucesso references=%s retrieved_chunks=%s",
            request_id,
            refs_count,
            chunks_count,
        )
        return QuestionResponse(**result)
    except Exception:
        logger.exception("request_id=%s | falha no processamento da pergunta", request_id)
        raise
