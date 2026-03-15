"""
Configuração central de logging da aplicação.
"""
import logging
import sys


LOG_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
_configured = False


def setup_logging(level: str = "INFO") -> None:
    """Configura o logging global da aplicação. Evita duplicar handlers em chamadas repetidas."""
    global _configured
    if _configured:
        return
    log_level = getattr(logging, level.upper(), logging.INFO)
    if not isinstance(log_level, int):
        log_level = logging.INFO
    formatter = logging.Formatter(LOG_FORMAT)
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    app_logger = logging.getLogger("app")
    app_logger.setLevel(log_level)
    app_logger.handlers.clear()
    app_logger.addHandler(handler)
    app_logger.propagate = False
    _configured = True


def get_logger(name: str) -> logging.Logger:
    """Retorna um logger com o nome dado (normalmente __name__ do módulo)."""
    return logging.getLogger(name)
