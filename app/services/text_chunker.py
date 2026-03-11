import uuid


def chunk_text(
    pages: list[dict],
    source: str,
    chunk_size: int = 1000,
    overlap: int = 150,
    min_chunk_length: int = 120,
) -> list[dict]:
    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size")

    chunks = []

    for page in pages:
        text = page["text"]
        page_number = page["page"]

        if not text:
            continue

        start = 0
        text_length = len(text)

        while start < text_length:
            end = start + chunk_size
            chunk = text[start:end].strip()

            if len(chunk) >= min_chunk_length:
                chunks.append(
                    {
                        "chunk_id": str(uuid.uuid4()),
                        "text": chunk,
                        "page": page_number,
                        "source": source,
                    }
                )

            step = chunk_size - overlap
            start += step

    return chunks