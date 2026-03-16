"""
Decorators que concentram o logging nos pipelines e no vector store.
"""
import functools
import time

from app.core.logging import get_logger

logger = get_logger("app.core.log_decorators")


def _truncate(s: str, max_len: int = 80) -> str:
    if len(s) <= max_len:
        return s
    return s[:max_len] + "..."


def log_ingestion_run(fn):
    """Decorator para IngestionPipeline.run: log início, execução, métricas e elapsed."""
    @functools.wraps(fn)
    def wrapper(self, file_path: str, source_name: str, request_id: str | None = None, **kwargs):
        rid = request_id or ""
        logger.info(
            "request_id=%s | ingestion pipeline início file_path=%s source_name=%s",
            rid,
            file_path,
            source_name,
        )
        t0 = time.perf_counter()
        result = fn(self, file_path, source_name, request_id=request_id, **kwargs)
        elapsed = time.perf_counter() - t0
        if isinstance(result, dict) and "_log" in result:
            m = result.pop("_log")
            logger.info(
                "request_id=%s | pipeline concluído pages=%s chunks=%s embeddings=%s persisted=%s elapsed=%.3fs",
                rid,
                m.get("pages"),
                m.get("chunks"),
                m.get("embeddings"),
                m.get("persisted"),
                elapsed,
            )
        else:
            logger.info(
                "request_id=%s | pipeline concluído total_chunks=%s elapsed=%.3fs",
                rid,
                result.get("total_chunks", 0),
                elapsed,
            )
        return result
    return wrapper


def log_question_run(fn):
    """Decorator para QuestionPipeline.run: log início, execução, métricas e elapsed."""
    @functools.wraps(fn)
    def wrapper(
        self,
        question: str,
        top_k=None,
        initial_k=None,
        max_distance=None,
        min_score=None,
        request_id: str | None = None,
        **kwargs,
    ):
        rid = request_id or ""
        logger.info(
            "request_id=%s | question pipeline início pergunta=%s",
            rid,
            _truncate(question),
        )
        t0 = time.perf_counter()
        result = fn(
            self,
            question=question,
            top_k=top_k,
            initial_k=initial_k,
            max_distance=max_distance,
            min_score=min_score,
            request_id=request_id,
            **kwargs,
        )
        elapsed = time.perf_counter() - t0
        if isinstance(result, dict) and "_log" in result:
            m = result.pop("_log")
            logger.info(
                "request_id=%s | pipeline concluído retrieved=%s references=%s elapsed=%.3fs",
                rid,
                m.get("retrieved"),
                m.get("references"),
                elapsed,
            )
        else:
            refs = len(result.get("references") or [])
            logger.info(
                "request_id=%s | pipeline concluído references=%s elapsed=%.3fs",
                rid,
                refs,
                elapsed,
            )
        return result
    return wrapper


def log_vector_store_add(fn):
    """Decorator para VectorStore.add_vectors: log quantidade após a chamada."""
    @functools.wraps(fn)
    def wrapper(self, ids, embeddings, documents):
        result = fn(self, ids, embeddings, documents)
        logger.info("add_vectors quantidade=%s", len(result))
        return result
    return wrapper


def log_vector_store_search(fn):
    """Decorator para VectorStore.query_nearest: log k e resultados."""
    @functools.wraps(fn)
    def wrapper(self, query_embedding, k: int = 8):
        result = fn(self, query_embedding, k)
        logger.info("query_nearest k=%s resultados=%s", k, len(result))
        return result
    return wrapper
