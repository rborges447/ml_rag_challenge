from fastapi import FastAPI

from app.api import documents_router, questions_router
from app.core.config import settings
from app.core.logging import setup_logging

app = FastAPI(
    title="ML Engineering Challenge - RAG API",
    version="0.1.0",
)


@app.on_event("startup")
def on_startup() -> None:
    setup_logging(level=settings.log_level)


app.include_router(documents_router)
app.include_router(questions_router)


@app.get("/health")
def healthcheck() -> dict:
    return {"status": "ok"}
