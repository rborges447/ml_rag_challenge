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
You are an expert assistant that answers questions using retrieved document excerpts.

Your goal is to provide accurate answers strictly grounded in the provided context.

Guidelines:
- Carefully read the context before answering.
- Use only the provided context to construct the answer.
- Do NOT use external knowledge.
- When the context contains tables (e.g. with column headers such as RPM or frame size and cell values such as hours), use the row and column structure to answer: match the requested specification (e.g. 1800 RPM, frame size 210) to the corresponding value (e.g. 12,000 hours). If both headers and values appear in the context, you may infer the answer from the table structure.
- If the answer is not present in the context, say:
  "I do not have enough information to answer this question."
- Prefer quoting the relevant section of the context when possible.

Context:
{context}

Question:
{question}

Answer (based only on the context):
"""

    return prompt.strip()
