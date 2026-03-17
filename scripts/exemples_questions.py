import sys
from pathlib import Path

# garantir import de app
root = Path(__file__).resolve().parent.parent
if str(root) not in sys.path:
    sys.path.insert(0, str(root))

from app.pipelines import QuestionPipeline

EXAMPLE_CASES = [
    {
        "pdf_name": "LB5001.pdf",
        "question": "How often should motor bearings be lubricated for motors up to frame size 210 at 1800 RPM?",
        "expected": "Motor bearings for motors up to frame size 210 at 1800 RPM should be relubricated every 12,000 hours.",
        "keywords": ["12000", "12,000", "hours"],
    },
    {
        "pdf_name": "MN414_0224.pdf",
        "question": "What lubricant is recommended for new Baldor submersible motors?",
        "expected": "The recommended lubricant is Shell Rotella 10 SAE 10W. The manual also states that new Baldor submersible motors ship with the oil reservoir properly filled with lubricant.",
        "keywords": ["shell rotella", "10w"],
    },
    {
        "pdf_name": "WEG-CESTARI-manual-iom-guia-consulta-rapida-50111652-pt-en-es-web.pdf",
        "question": "Within what maximum period must WEG-CESTARI gear units or gearmotors be put into operation after leaving the factory?",
        "expected": "WEG-CESTARI gear units and gearmotors must be put into operation within a maximum period of 6 months after leaving the factory.",
        "keywords": ["6 months", "six months"],
    },
    {
        "pdf_name": "WEG-motores-eletricos-guia-de-especificacao-50032749-brochure-portuguese-web.pdf",
        "question": "Por que o motor de indução é o tipo de motor elétrico mais utilizado?",
        "expected": "O motor de indução é o mais utilizado porque possui construção simples, alta confiabilidade, baixo custo, baixa necessidade de manutenção e boa eficiência, o que o torna adequado para uma ampla variedade de aplicações industriais.",
        "keywords": ["construção simples", "confiabilidade", "baixo custo", "manutenção", "eficiência"],
    },
]


def _matches(answer: str, keywords: list[str]) -> tuple[bool, list[str]]:
    text = (answer or "").lower()
    missing = [k for k in keywords if k.lower() not in text]
    return (len(missing) == 0, missing)


def main() -> None:
    pipeline = QuestionPipeline()
    ok_count = 0

    for case in EXAMPLE_CASES:
        print("=" * 80)
        print(f"PDF: {case['pdf_name']}")
        print(f"Pergunta: {case['question']}")
        out = pipeline.run(case["question"], top_k=5)
        answer = out.get("answer", "")
        print(f"\nResposta do sistema:\n{answer}\n")
        print(f"Resposta esperada:\n{case['expected']}\n")

        is_ok, missing = _matches(answer, case["keywords"])
        if is_ok:
            ok_count += 1
            print("Match aproximado: OK")
        else:
            print(f"Match aproximado: FALHOU (faltou: {', '.join(missing)})")

    print("=" * 80)
    print(f"Resumo: {ok_count}/{len(EXAMPLE_CASES)} exemplos com match aproximado OK")


if __name__ == "__main__":
    main()