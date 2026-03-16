"""
Ferramenta de debug para inspeção do retrieval.

Uso (a partir da raiz do projeto):

    python scripts/debug_retrieval.py "Sua pergunta aqui"

Mostra:
- pergunta
- parâmetros usados (top_k, initial_k)
- chunks recuperados com:
  - índice
  - score e rerank_score
  - source / page / chunk_index / char_count / section_hint
  - preview de texto
"""

import sys
from pathlib import Path
from typing import Iterable

# Garante que o projeto está em sys.path ao rodar "python scripts/debug_retrieval.py"
_root = Path(__file__).resolve().parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from app.pipelines import QuestionPipeline


def _print_chunk(idx: int, chunk: dict, evidence_substrings: Iterable[str] | None = None) -> None:
    text = (chunk.get("text") or "").strip()
    source = chunk.get("source")
    page = chunk.get("page")
    distance = chunk.get("distance")
    score = chunk.get("score")
    rerank_score = chunk.get("rerank_score")
    chunk_index = chunk.get("chunk_index")
    char_count = chunk.get("char_count")
    section_hint = chunk.get("section_hint")

    preview = text[:400].replace("\n", " ").strip()
    has_evidence = False
    if evidence_substrings:
        lower = text.lower()
        for ev in evidence_substrings:
            if ev and ev.lower() in lower:
                has_evidence = True
                break

    ev_flag = "EVIDENCE" if has_evidence else ""
    print(f"--- Chunk #{idx} {ev_flag}")
    print(f"source={source!r} page={page} chunk_index={chunk_index} char_count={char_count}")
    print(f"distance={distance:.4f} score={score:.4f} rerank_score={rerank_score:.4f}")
    if section_hint:
        print(f"section_hint={section_hint!r}")
    print(f"text_preview={preview!r}")
    print()


def debug_question(
    question: str,
    top_k: int = 5,
    initial_k: int | None = None,
    evidence_substrings: Iterable[str] | None = None,
) -> None:
    pipeline = QuestionPipeline()

    print("=" * 80)
    print(f"QUESTION: {question}")
    print(f"(top_k={top_k}, initial_k={initial_k or 'default'})")
    print("=" * 80)

    result = pipeline.run(
        question=question,
        top_k=top_k,
        initial_k=initial_k,
    )

    chunks = result.get("retrieved_chunks") or []
    print(f"Total retrieved_chunks={len(chunks)}")
    print()

    for i, chunk in enumerate(chunks):
        _print_chunk(i, chunk, evidence_substrings=evidence_substrings)


def main() -> None:
    if len(sys.argv) < 2:
        print("Uso:")
        print("  python scripts/debug_retrieval.py \"Pergunta aqui\"")
        raise SystemExit(1)

    question = sys.argv[1]
    debug_question(question)


if __name__ == "__main__":
    main()

