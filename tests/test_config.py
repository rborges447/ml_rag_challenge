from app.core.config import settings

print("chroma_path:", settings.chroma_path)
print("chunk_size:", settings.chunk_size)
print("retrieval_initial_k:", settings.retrieval_initial_k)
print("llm providers:", settings.llm_provider_list)
print("gemini model:", settings.gemini_model)
print("gemini key loaded:", bool(settings.gemini_api_key))