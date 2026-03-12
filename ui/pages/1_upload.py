import streamlit as st

from ui.services import api_client
from ui.state import session_state as ui_state
from ui.utils.validators import is_valid_pdf, validate_file_size


def main() -> None:
    ui_state.init_session_state()

    st.title("Upload de documentos")

    uploaded_files = st.file_uploader(
        "Envie seus PDFs",
        type=["pdf"],
        accept_multiple_files=True,
    )

    if st.button("Indexar PDFs") and uploaded_files:
        for f in uploaded_files:
            if not is_valid_pdf(f):
                ui_state.add_upload_feedback(
                    {"file": f.name, "status": "erro", "detail": "Arquivo não é um PDF válido."}
                )
                continue
            if not validate_file_size(f):
                ui_state.add_upload_feedback(
                    {"file": f.name, "status": "erro", "detail": "Arquivo muito grande."}
                )
                continue

            data, error = api_client.upload_document(f)
            if error:
                ui_state.add_upload_feedback(
                    {"file": f.name, "status": "erro", "detail": error}
                )
            else:
                ui_state.add_upload_feedback(
                    {
                        "file": f.name,
                        "status": "ok",
                        "detail": data,
                    }
                )

    for entry in st.session_state.get("upload_feedback", []):
        if entry["status"] == "ok":
            st.success(f"{entry['file']}: indexado com sucesso.")
        else:
            st.error(f"{entry['file']}: {entry['detail']}")


if __name__ == "__main__":
    main()

