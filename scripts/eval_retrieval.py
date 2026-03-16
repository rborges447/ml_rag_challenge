"""
Avaliação simples de retrieval baseada em perguntas pré-definidas.

Uso (a partir da raiz do projeto):

    python scripts/eval_retrieval.py

Para cada pergunta:
- executa QuestionPipeline.run com top_k fixo;
- verifica se ao menos um chunk contém a evidência esperada;
- reporta métricas top1 / top3 / top5.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List


def _ensure_app_on_path() -> None:
    root = Path(__file__).resolve().parent.parent
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))


_ensure_app_on_path()

from app.pipelines import QuestionPipeline  # noqa: E402


@dataclass
class EvalCase:
    question: str
    expected_answer: str
    evidence_substrings: List[str]


CASES: List[EvalCase] = [
    EvalCase(
        question="What should be done before accepting a motor delivery?",
        expected_answer=(
            "The motor should be inspected for damage before accepting it, "
            "and the shaft should rotate freely with no rubs."
        ),
        evidence_substrings=[
            "inspected for damage before accepting",
            "shaft should rotate freely",
            "no rubs",
        ],
    ),
    EvalCase(
        question="What should be done if a motor does not start smoothly?",
        expected_answer=(
            "The motor should be stopped immediately and the cause investigated. "
            "Possible causes include low voltage, incorrect motor connections, or excessive load."
        ),
        evidence_substrings=[
            "stopped immediately",
            "cause investigated",
            "low voltage",
            "incorrect motor connections",
            "excessive load",
        ],
    ),
    EvalCase(
        question="How often should bearings be lubricated for motors up to frame size 210 at 1800 RPM?",
        expected_answer="12,000 hours.",
        evidence_substrings=["12,000 hours", "12000 hours"],
    ),
    EvalCase(
        question="What is the recommended lubricant for new Baldor submersible motors?",
        expected_answer="Shell Rotella 10 SAE 10W.",
        evidence_substrings=[
            "Shell Rotella 10 SAE 10W",
            "Rotella 10 SAE 10W",
        ],
    ),
    EvalCase(
        question="What can happen if thermal protectors are not connected?",
        expected_answer=(
            "The motor may lose over-temperature protection and unsafe operating conditions may occur."
        ),
        evidence_substrings=[
            "lose over-temperature protection",
            "unsafe operating conditions",
        ],
    ),
    EvalCase(
        question="What should be used to lift a submersible motor?",
        expected_answer=(
            "Only the lifting eyes provided should be used; the motor must never be lifted by the power cords."
        ),
        evidence_substrings=[
            "Only the lifting eyes",
            "never be lifted by the power cords",
        ],
    ),
    EvalCase(
        question=(
            "What is the maximum recommended time for a fully loaded and uncovered submersible "
            "motor to operate while drawing the well down?"
        ),
        expected_answer="It should not be greater than 15 minutes.",
        evidence_substrings=["not be greater than 15 minutes", "15 minutes"],
    ),
    EvalCase(
        question="What is the standard frequency of industrial three-phase power in Brazil according to the WEG guide?",
        expected_answer="60 Hz.",
        evidence_substrings=["60 Hz", "60hz"],
    ),
    EvalCase(
        question="What is the formula for active power in a three-phase system with reactive load?",
        expected_answer="P = √3 × U × I × cos φ.",
        evidence_substrings=[
            "P = √3 × U × I × cos φ",
            "P = 3**0.5",
            "P = sqrt(3) x U x I x cos",
        ],
    ),
    EvalCase(
        question="What is slip in an induction motor?",
        expected_answer=(
            "Slip is the difference between motor speed and synchronous speed, "
            "usually expressed as a fraction or percentage of synchronous speed."
        ),
        evidence_substrings=[
            "difference between motor speed and synchronous speed",
            "expressed as a fraction or percentage of synchronous speed",
        ],
    ),
    # Perguntas adicionais fornecidas para avaliação
    EvalCase(
        question="What is the recommended lubrication interval for motors at 1800 RPM?",
        expected_answer="(interval in hours, dependent on frame size; e.g. 12,000 hours for smaller frames).",
        evidence_substrings=["1800", "RPM", "hours"],
    ),
    EvalCase(
        question="What should be checked if a motor does not run smoothly?",
        expected_answer=(
            "The motor should be checked for low voltage, incorrect connections, misalignment, "
            "and excessive or uneven load."
        ),
        evidence_substrings=["low voltage", "incorrect", "connections", "excessive load", "misalignment"],
    ),
    EvalCase(
        question="What safety precautions should be taken when installing a motor?",
        expected_answer=(
            "Follow all lockout/tagout procedures, ensure the motor is properly grounded, "
            "and avoid lifting the motor by the power leads or fan."
        ),
        evidence_substrings=["lockout", "tagout", "properly grounded", "lifted by the power cords", "power leads"],
    ),
]


def _chunk_has_evidence(text: str, evidence: Iterable[str]) -> bool:
    if not text:
        return False
    lower = text.lower()
    return any(ev and ev.lower() in lower for ev in evidence)


def evaluate_case(pipeline: QuestionPipeline, case: EvalCase, top_k: int = 5) -> dict:
    result = pipeline.run(question=case.question, top_k=top_k)
    chunks = result.get("retrieved_chunks") or []
    texts = [c.get("text", "") or "" for c in chunks]

    def has_evidence_at(k: int) -> bool:
        sub = texts[:k]
        return any(_chunk_has_evidence(t, case.evidence_substrings) for t in sub)

    return {
        "question": case.question,
        "top1_ok": has_evidence_at(1),
        "top3_ok": has_evidence_at(min(3, len(texts))),
        "top5_ok": has_evidence_at(min(5, len(texts))),
        "num_chunks": len(chunks),
    }


def main() -> None:
    pipeline = QuestionPipeline()
    print("Avaliação de retrieval (evidência em top-1 / top-3 / top-5)")
    print("=" * 80)

    results = [evaluate_case(pipeline, case, top_k=5) for case in CASES]

    for r in results:
        q_preview = r["question"][:70] + ("..." if len(r["question"]) > 70 else "")
        t1 = "ok" if r["top1_ok"] else "  "
        t3 = "ok" if r["top3_ok"] else "  "
        t5 = "ok" if r["top5_ok"] else "  "
        print(f"- {q_preview}")
        print(f"    top-1: {t1}  top-3: {t3}  top-5: {t5}  (chunks: {r['num_chunks']})")

    print("=" * 80)
    n = len(results)
    top1_count = sum(1 for r in results if r["top1_ok"])
    top3_count = sum(1 for r in results if r["top3_ok"])
    top5_count = sum(1 for r in results if r["top5_ok"])
    print(f"Resumo: top-1 {top1_count}/{n}  top-3 {top3_count}/{n}  top-5 {top5_count}/{n}")


if __name__ == "__main__":
    main()

