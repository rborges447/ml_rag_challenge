"""
Pré-processamento de texto extraído de PDF: normalização, ruído, cabeçalhos/rodapés.
"""
import re
from typing import Any


GENERIC_PHRASES = frozenset({
    "sumário", "sumario", "índice", "indice", "introdução", "introducao",
    "página", "pagina", "capítulo", "capitulo", "cap.", "pág.", "pag.",
})


def normalize_text(text: str) -> str:
    if not text:
        return ""
    text = text.replace("\x00", " ")
    text = text.replace("\r\n", "\n").replace("\r", "\n").replace("\t", " ")
    lines = text.split("\n")
    cleaned = [re.sub(r" +", " ", line).strip() for line in lines]
    text = "\n".join(cleaned)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def remove_noise_lines(
    lines: list[str],
    min_line_len: int = 3,
    drop_number_only: bool = True,
    drop_punctuation_only: bool = True,
) -> list[str]:
    result = []
    for line in lines:
        s = line.strip()
        if len(s) < min_line_len:
            continue
        if drop_number_only and re.match(r"^\d+\.?\s*$", s):
            continue
        if drop_punctuation_only and re.match(r"^[\s\.\,\-\;\:\_]+$", s):
            continue
        result.append(line)
    return result


def _line_fingerprint(line: str, max_len: int = 80) -> str:
    s = line.strip()[:max_len].lower()
    return re.sub(r"\s+", " ", s)


def remove_repeated_headers_footers(
    pages: list[dict[str, Any]],
    threshold: float = 0.5,
    max_line_len: int = 80,
) -> list[dict[str, Any]]:
    if not pages:
        return pages
    line_counts: dict[str, int] = {}
    for p in pages:
        text = p.get("text", "") or ""
        seen_this_page: set[str] = set()
        for line in text.split("\n"):
            fp = _line_fingerprint(line, max_line_len)
            if len(fp) < 3 or len(line.strip()) > max_line_len:
                continue
            if fp not in seen_this_page:
                seen_this_page.add(fp)
                line_counts[fp] = line_counts.get(fp, 0) + 1
    n_pages = len(pages)
    cutoff = max(2, int(n_pages * threshold))
    repeated = {fp for fp, c in line_counts.items() if c >= cutoff}

    def filter_lines(text: str) -> str:
        out = [line for line in text.split("\n") if _line_fingerprint(line, max_line_len) not in repeated]
        return "\n".join(out)

    return [{"page": p["page"], "text": filter_lines(p.get("text", "") or "")} for p in pages]


def remove_generic_only_blocks(text: str) -> str:
    blocks = text.split("\n\n")
    result = []
    for block in blocks:
        stripped = block.strip()
        if not stripped:
            continue
        lines = [ln.strip().lower() for ln in stripped.split("\n") if ln.strip()]
        if not lines:
            continue
        if len(lines) == 1 and any(phrase in lines[0] for phrase in GENERIC_PHRASES) and len(stripped) < 60:
            continue
        result.append(block)
    return "\n\n".join(result)


def preprocess_pages(
    pages: list[dict[str, Any]],
    header_footer_threshold: float = 0.5,
) -> list[dict[str, Any]]:
    out = []
    for p in pages:
        text = p.get("text", "") or ""
        text = normalize_text(text)
        lines = remove_noise_lines(text.split("\n"))
        text = "\n".join(lines)
        text = remove_generic_only_blocks(text)
        text = re.sub(r"\n{3,}", "\n\n", text).strip()
        out.append({"page": p["page"], "text": text})
    return remove_repeated_headers_footers(out, threshold=header_footer_threshold)


class TextPreprocessor:
    """Encapsula o pipeline de pré-processamento de páginas."""

    def preprocess_pages(
        self,
        pages: list[dict[str, Any]],
        header_footer_threshold: float = 0.5,
    ) -> list[dict[str, Any]]:
        return preprocess_pages(pages, header_footer_threshold=header_footer_threshold)
