"""
Expansão leve de query para melhorar retrieval cross-lingual (EN ↔ PT).
Adiciona termos em português quando a pergunta está em inglês, para aumentar
a chance de match com documentos em PT (ex.: manual WEG).
"""
import re
import unicodedata

# Mapeamento de termos técnicos EN → PT (editável). Chaves em minúsculas.
QUERY_EXPANSION_EN_TO_PT: dict[str, str] = {
    "induction motor": "motor de indução motores de indução",
    "induction motors": "motores de indução motor de indução",
    "electric motor": "motor elétrico",
    "electric motors": "motores elétricos",
    "widely used": "mais utilizado mais utilizados",
    "most widely used": "mais utilizado mais utilizados",
    "most common": "mais comum mais comuns",
    "bearing": "rolamento",
    "bearings": "rolamentos",
    "lubrication": "lubrificação relubrificação",
    "lubricated": "lubrificado",
    "relubrication": "relubrificação",
    "frame size": "tamanho de quadro frame",
    "submersible motor": "motor submerso",
    "submersible motors": "motores submersos",
    "three-phase": "trifásico trifásicos",
    "single-phase": "monofásico",
    "efficiency": "eficiência rendimento",
    "reliability": "confiabilidade",
    "maintenance": "manutenção",
    "construction": "construção",
    "advantages": "vantagens",
    "benefits": "benefícios vantagens",
}


def _normalize(s: str) -> str:
    if not s:
        return ""
    s = s.lower().strip()
    nfd = unicodedata.normalize("NFD", s)
    return "".join(c for c in nfd if unicodedata.category(c) != "Mn")


def expand_query_for_embed(question: str) -> str:
    """
    Retorna a query com termos em PT concatenados ao final, para melhorar
    a similaridade com documentos em português. A query original é mantida
    intacta; os termos PT são adicionados após um espaço.
    """
    if not question or not question.strip():
        return question
    q_lower = question.lower()
    q_norm = _normalize(question)
    added: list[str] = []
    for en_term, pt_terms in QUERY_EXPANSION_EN_TO_PT.items():
        en_norm = _normalize(en_term)
        if en_norm in q_norm or en_term in q_lower:
            for pt in pt_terms.split():
                pt = pt.strip()
                if pt and pt not in added:
                    added.append(pt)
    if not added:
        return question
    return question.strip() + " " + " ".join(added)
