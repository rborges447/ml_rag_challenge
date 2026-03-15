from app.qa.prompt_builder import build_prompt


def test_build_prompt_includes_question_and_context() -> None:
    question = "O que é um título público?"
    chunks = [
        {"text": "Um título público é um instrumento de dívida emitido pelo governo.", "source": "doc1", "page": 1},
        {"text": "Títulos públicos são usados para financiar a dívida pública.", "source": "doc1", "page": 2},
    ]

    prompt = build_prompt(question, chunks)

    assert "O que é um título público?" in prompt
    assert "Um título público é um instrumento de dívida emitido pelo governo." in prompt
    assert "Títulos públicos são usados para financiar a dívida pública." in prompt

