# ML RAG Challenge

## Reindexação

Após mudanças no chunking ou na limpeza de texto, os embeddings antigos não refletem a nova estratégia. Para reindexar:

1. Apague o diretório `data/chroma` (ou o conteúdo dele).
2. Reenvie os PDFs via `POST /documents` para cada arquivo que deve estar no índice (os PDFs em `data/raw` continuam válidos; o serviço reextrai, rechunka e reembarca).
