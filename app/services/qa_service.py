"""
Serviço de Q&A preparado para futura integração de LLM.
Hoje o fluxo expõe apenas retrieved_chunks via POST /question.
Quando integrar geração: orquestrar retrieval + prompt + LLM e retornar resposta natural.
"""
