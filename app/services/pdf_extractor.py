import re

import fitz


def clean_text(text: str) -> str:
    text = text.replace("\x00", " ")
    text = text.replace("\r", " ")
    text = text.replace("\t", " ")
    text = text.replace("\n", " ")

    text = re.sub(r"\s+", " ", text)
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