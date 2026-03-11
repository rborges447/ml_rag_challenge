import re
import uuid


def _split_into_blocks(text: str) -> list[str]:
    """Divide o texto em blocos por quebras de linha (parágrafos ou linhas)."""
    text = text.strip()
    if not text:
        return []
    blocks = re.split(r"\n+", text)
    return [b.strip() for b in blocks if b.strip()]


def chunk_text(
    pages: list[dict],
    source: str,
    target_chunk_chars: int = 1000,
    max_chunk_chars: int = 1400,
    min_block_chars: int = 50,
    overlap_blocks: int = 1,
) -> list[dict]:
    """
    Gera chunks baseados em blocos/parágrafos, preservando estrutura do texto.
    - Agrupa blocos até atingir target_chunk_chars, sem ultrapassar max_chunk_chars.
    - Descarta blocos muito curtos (menos de min_block_chars).
    - Overlap natural: os últimos overlap_blocks do chunk anterior iniciam o próximo.
    """
    if overlap_blocks < 0:
        raise ValueError("overlap_blocks must be >= 0")
    if min_block_chars <= 0 or target_chunk_chars <= 0 or max_chunk_chars < target_chunk_chars:
        raise ValueError("invalid chunk size or block constraints")

    chunks = []

    for page in pages:
        text = page["text"]
        page_number = page["page"]

        if not text:
            continue

        blocks = _split_into_blocks(text)
        blocks = [b for b in blocks if len(b) >= min_block_chars]

        if not blocks:
            continue

        i = 0
        while i < len(blocks):
            current_blocks = []
            current_len = 0

            while i < len(blocks) and current_len + len(blocks[i]) + (1 if current_blocks else 0) <= max_chunk_chars:
                sep = "\n" if current_blocks else ""
                current_blocks.append(blocks[i])
                current_len += len(sep) + len(blocks[i])
                i += 1
                if current_len >= target_chunk_chars:
                    break

            if not current_blocks:
                i += 1
                continue

            chunk_text_content = "\n".join(current_blocks)
            chunks.append(
                {
                    "chunk_id": str(uuid.uuid4()),
                    "text": chunk_text_content,
                    "page": page_number,
                    "source": source,
                }
            )

            if overlap_blocks > 0 and i < len(blocks):
                i -= overlap_blocks
                i = max(i, 0)

    return chunks
