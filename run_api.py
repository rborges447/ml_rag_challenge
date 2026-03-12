import uvicorn


def main() -> None:
    """Inicia o servidor FastAPI da aplicação."""
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )


if __name__ == "__main__":
    main()

