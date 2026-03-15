from pydantic import BaseModel, Field


class QuestionRequest(BaseModel):
    question: str = Field(..., min_length=1)


class QuestionResponse(BaseModel):
    answer: str
    references: list[str]
    retrieved_chunks: list[dict] | None = None
