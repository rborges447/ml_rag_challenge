import re

import fitz


def clean_text(text: str) -> str:
    """
    Limpa o texto preservando quebras de linha para chunking semântico.
    - Normaliza fim de linha (\\r\\n, \\r) para \\n
    - Remove/substitui caracteres problemáticos (\\x00, \\t)
    - Colapsa múltiplos espaços dentro de cada linha (não cruza \\n)
    - Normaliza múltiplas quebras consecutivas para no máximo \\n\\n
    """
    if not text:
        return ""

    text = text.replace("\x00", " ")
    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")
    text = text.replace("\t", " ")

    lines = text.split("\n")
    cleaned_lines = []
    for line in lines:
        line = re.sub(r" +", " ", line).strip()
        cleaned_lines.append(line)

    text = "\n".join(cleaned_lines)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def extract_text_from_pdf(file_path: str) -> list[dict]:
    """
    Extrai o texto de cada página de um PDF e aplica limpeza básica.

    Retorno:
    [
        {"page": 1, "text": "..."},
        {"page": 2, "text": "..."}
    ]
    """
    pages = []

    with fitz.open(file_path) as doc:
        for page_num, page in enumerate(doc, start=1):
            raw_text = page.get_text() or ""
            cleaned_text = clean_text(raw_text)

            if cleaned_text:
                pages.append(
                    {
                        "page": page_num,
                        "text": cleaned_text,
                    }
                )

    return pages
