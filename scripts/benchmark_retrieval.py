"""
Benchmark simples de retrieval: perguntas fixas, métricas top-1 / top-3 / top-5.
Critério de acerto: chunk no top-K contém todos os termos obrigatórios da pergunta.
Execute a partir da raiz do projeto: python scripts/benchmark_retrieval.py
Requer Chroma já indexado (POST /documents com um PDF antes).
"""
import sys
from pathlib import Path

# Garantir que o app seja importável
_root = Path(__file__).resolve().parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from app.services.pipelines import RetrievalPipeline


# Perguntas e termos que devem aparecer em pelo menos um chunk relevante (minúsculas)
BENCHMARK_QUESTIONS = [
    {
        "question": "o que é motor elétrico",
        "required_terms": ["motor elétrico", "motores elétricos"],
    },
    {
        "question": "o que é conjugado",
        "required_terms": ["conjugado"],
    },
    {
        "question": "quais são os tipos de motores elétricos",
        "required_terms": ["motores elétricos", "tipos"],
    },
    {
        "question": "o que é motor síncrono",
        "required_terms": ["motor síncrono", "síncrono"],
    },
    {
        "question": "como variar a velocidade de um motor de indução",
        "required_terms": ["velocidade", "motor", "indução"],
    },
]


def _chunk_is_relevant(chunk_text: str, required_terms: list[str]) -> bool:
    """True se o chunk contém todos os termos obrigatórios (case-insensitive)."""
    lower = chunk_text.lower()
    return all(term.lower() in lower for term in required_terms)


def run_benchmark(top_k: int = 5) -> list[dict]:
    """
    Para cada pergunta, chama retrieval com top_k=top_k e verifica top-1, top-3, top-5.
    Retorna lista de resultados por pergunta.
    """
    pipeline = RetrievalPipeline()
    results = []

    for item in BENCHMARK_QUESTIONS:
        question = item["question"]
        required = item["required_terms"]
        chunks = pipeline.run(question, top_k=top_k)
        texts = [c.get("text", "") or "" for c in chunks]

        top1 = len(texts) >= 1 and _chunk_is_relevant(texts[0], required)
        top3 = any(_chunk_is_relevant(t, required) for t in texts[:3]) if len(texts) >= 1 else False
        top5 = any(_chunk_is_relevant(t, required) for t in texts[:5]) if len(texts) >= 1 else False

        results.append({
            "question": question,
            "top1_ok": top1,
            "top3_ok": top3,
            "top5_ok": top5,
            "num_chunks": len(chunks),
        })

    return results


def main() -> None:
    print("Benchmark de retrieval (top-1, top-3, top-5)")
    print("=" * 60)
    results = run_benchmark(top_k=5)
    for r in results:
        q = r["question"][:50] + ("..." if len(r["question"]) > 50 else "")
        t1 = "ok" if r["top1_ok"] else "  "
        t3 = "ok" if r["top3_ok"] else "  "
        t5 = "ok" if r["top5_ok"] else "  "
        print(f"  {q}")
        print(f"    top-1: {t1}  top-3: {t3}  top-5: {t5}  (chunks: {r['num_chunks']})")
    print("=" * 60)
    top1_count = sum(1 for r in results if r["top1_ok"])
    top3_count = sum(1 for r in results if r["top3_ok"])
    top5_count = sum(1 for r in results if r["top5_ok"])
    n = len(results)
    print(f"Resumo: top-1 {top1_count}/{n}  top-3 {top3_count}/{n}  top-5 {top5_count}/{n}")


if __name__ == "__main__":
    main()
