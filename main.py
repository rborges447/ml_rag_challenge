"""
Ponto de entrada de conveniência para desenvolvimento local.

Este script inicia a API FastAPI e, em seguida, abre a interface Streamlit.
Em produção, recomenda-se rodar API e frontend com processos/serviços separados.
"""

import subprocess
import sys


def main() -> None:
    api_cmd = [sys.executable, "run_api.py"]
    streamlit_cmd = ["streamlit", "run", "streamlit_app.py"]

    api_process = subprocess.Popen(api_cmd)
    try:
        subprocess.run(streamlit_cmd, check=False)
    finally:
        api_process.terminate()


if __name__ == "__main__":
    main()

