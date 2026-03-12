from app.core.dependencies import get_embedding_function, get_vector_store


def test_get_embedding_function_singleton() -> None:
    emb1 = get_embedding_function()
    emb2 = get_embedding_function()
    assert emb1 is emb2


def test_get_vector_store_singleton() -> None:
    vs1 = get_vector_store()
    vs2 = get_vector_store()
    assert vs1 is vs2

