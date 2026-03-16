"""
Carrega PDF com PyMuPDF de forma table-aware: extrai tabelas com find_tables()
como blocos únicos (cabeçalho + linhas) e o texto restante da página separadamente,
para preservar estrutura de tabelas no RAG.
"""
from __future__ import annotations

from typing import Any

import fitz


def _rects_overlap(r1: tuple[float, float, float, float], r2: tuple[float, float, float, float]) -> bool:
    """True se os retângulos (x0, y0, x1, y1) se sobrepõem."""
    if r1 is None or r2 is None:
        return False
    x0_1, y0_1, x1_1, y1_1 = r1
    x0_2, y0_2, x1_2, y1_2 = r2
    if x1_1 <= x0_2 or x1_2 <= x0_1 or y1_1 <= y0_2 or y1_2 <= y0_1:
        return False
    return True


def _block_text_from_dict(block: dict) -> str:
    """Extrai texto de um bloco no formato get_text('dict')."""
    lines = []
    for line in block.get("lines", []):
        line_text = "".join(span.get("text", "") for span in line.get("spans", []))
        if line_text.strip():
            lines.append(line_text)
    return "\n".join(lines)


def load_table_aware(file_path: str, source_name: str) -> list[dict[str, Any]]:
    """
    Carrega o PDF e retorna uma lista de blocos, cada um com:
    - page: int (1-based)
    - text: str
    - is_table: bool (True para blocos extraídos de tabelas)

    Tabelas são extraídas com find_tables() e convertidas para markdown (cabeçalho + linhas).
    O texto restante da página (fora dos bbox das tabelas) é extraído por blocos e
    concatenado, para evitar duplicação. Se find_tables() falhar ou não encontrar
    tabelas, usa fallback com texto plano da página.
    """
    result: list[dict[str, Any]] = []
    doc = fitz.open(file_path)
    try:
        for page_index in range(len(doc)):
            page = doc[page_index]
            page_num = page_index + 1
            table_bboxes: list[tuple[float, float, float, float]] = []
            table_texts: list[str] = []

            try:
                finder = page.find_tables()
                if finder.tables:
                    for table in finder.tables:
                        try:
                            # Extrair conteúdo da tabela enquanto o page está vivo
                            raw = table.to_markdown()
                            if raw and raw.strip():
                                table_texts.append(raw.strip())
                                bbox = table.bbox
                                if bbox is not None:
                                    table_bboxes.append(tuple(bbox))
                        except Exception:
                            continue
            except Exception:
                pass

            for tbl_text in table_texts:
                result.append({
                    "page": page_num,
                    "text": tbl_text,
                    "is_table": True,
                })

            try:
                d = page.get_text("dict")
                narrative_parts = []
                for block in d.get("blocks", []):
                    block_bbox = block.get("bbox")
                    if block_bbox is None:
                        narrative_parts.append(_block_text_from_dict(block))
                        continue
                    bbox_tuple = tuple(block_bbox)
                    if any(_rects_overlap(bbox_tuple, tb) for tb in table_bboxes):
                        continue
                    narrative_parts.append(_block_text_from_dict(block))
                narrative_text = "\n\n".join(p for p in narrative_parts if p.strip()).strip()
                if narrative_text:
                    result.append({
                        "page": page_num,
                        "text": narrative_text,
                        "is_table": False,
                    })
            except Exception:
                fallback = page.get_text()
                if fallback and fallback.strip() and not table_bboxes:
                    result.append({
                        "page": page_num,
                        "text": fallback.strip(),
                        "is_table": False,
                    })
    finally:
        doc.close()

    if not result:
        doc = fitz.open(file_path)
        try:
            for page_index in range(len(doc)):
                page = doc[page_index]
                page_num = page_index + 1
                text = page.get_text()
                if text and text.strip():
                    result.append({
                        "page": page_num,
                        "text": text.strip(),
                        "is_table": False,
                    })
        finally:
            doc.close()

    return result
