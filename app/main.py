from fastapi import FastAPI

from app.api import documents_router, questions_router

app = FastAPI(
    title="ML Engineering Challenge - RAG API",
    version="0.1.0",
)

app.include_router(documents_router)
app.include_router(questions_router)


@app.get("/health")
def healthcheck() -> dict:
    return {"status": "ok"}
