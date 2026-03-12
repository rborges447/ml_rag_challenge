from typing import Any


def is_valid_pdf(file_obj: Any) -> bool:
    """Valida se o arquivo parece ser um PDF."""
    content_type = getattr(file_obj, "type", None) or getattr(
        file_obj, "content_type", None
    )
    name = getattr(file_obj, "name", "") or ""
    return (
        (content_type == "application/pdf")
        or name.lower().endswith(".pdf")
    )


def validate_file_size(file_obj: Any, max_mb: int = 20) -> bool:
    """Valida tamanho máximo aproximado do arquivo em MB."""
    try:
        data = file_obj.getvalue()
    except Exception:  # noqa: BLE001
        return True
    size_mb = len(data) / (1024 * 1024)
    return size_mb <= max_mb

