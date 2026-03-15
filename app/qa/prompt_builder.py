def build_prompt(question: str, chunks: list[dict]) -> str:
    context_parts = []

    for chunk in chunks:
        text = chunk.get("text", "")
        source = chunk.get("source", "unknown")
        page = chunk.get("page", "?")

        context_parts.append(
            f"[Source: {source} | Page: {page}]\n{text}"
        )

    context = "\n\n".join(context_parts)

    prompt = f"""
You are a technical assistant.

Answer the question using ONLY the context provided below.
If the answer cannot be found in the context, say you do not have enough information.

Context:
{context}

Question:
{question}

Answer:
"""

    return prompt.strip()
