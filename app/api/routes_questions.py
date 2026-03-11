
from fastapi import APIRouter

from app.schemas.question import QuestionRequest
from app.services.retriever import Retriever

router = APIRouter(tags=["questions"])

retriever = Retriever()


@router.post("/question")
def ask_question(payload: QuestionRequest) -> dict:
    chunks = retriever.retrieve(payload.question, top_k=5)

    return {
        "question": payload.question,
        "retrieved_chunks": chunks,
    }
'''
from fastapi import APIRouter

from app.schemas.question import QuestionRequest, QuestionResponse

router = APIRouter(tags=["questions"])


@router.post("/question", response_model=QuestionResponse)
def ask_question(payload: QuestionRequest) -> QuestionResponse:
    return QuestionResponse(
        answer=f"Question received: {payload.question}",
        references=[],
    )
'''