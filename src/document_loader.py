"""
src/document_loader.py
----------------------
Responsável por ler PDFs e dividi-los em chunks (trechos).

Chunking é o processo de dividir um documento longo em pedaços
menores para que possam ser indexados e recuperados com precisão.
Um chunk muito grande perde foco. Um chunk muito pequeno perde contexto.
O tamanho padrão aqui (800 caracteres, 100 de sobreposição) é um bom
ponto de partida para documentos técnicos industriais.
"""

import fitz  # PyMuPDF
from langchain_text_splitters import RecursiveCharacterTextSplitter


def extract_text_from_pdf(pdf_bytes: bytes, filename: str) -> str:
    """
    Extrai o texto completo de um PDF em bytes.

    Parâmetros:
        pdf_bytes: conteúdo do PDF em bytes (vindo do st.file_uploader)
        filename: nome do arquivo (usado para mensagens de erro)

    Retorna:
        Texto extraído como string
    """
    try:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        text = ""
        for page_num, page in enumerate(doc):
            page_text = page.get_text()
            if page_text.strip():
                text += f"\n[Página {page_num + 1}]\n{page_text}"
        doc.close()
        return text
    except Exception as e:
        raise ValueError(f"Erro ao ler o PDF '{filename}': {str(e)}")


def split_into_chunks(text: str, filename: str) -> list[dict]:
    """
    Divide o texto em chunks sobrepostos para indexação.

    Por que RecursiveCharacterTextSplitter?
    Ele tenta dividir nos pontos naturais do texto (parágrafos,
    depois frases, depois palavras), evitando cortar no meio de
    uma informação importante.

    Parâmetros:
        text: texto completo extraído do PDF
        filename: nome do arquivo (usado como metadado em cada chunk)

    Retorna:
        Lista de dicionários com 'content' e 'source'
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,       # ~800 caracteres por chunk
        chunk_overlap=100,    # 100 caracteres de sobreposição entre chunks vizinhos
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    chunks_text = splitter.split_text(text)

    # Adiciona metadado de origem em cada chunk
    chunks = [
        {"content": chunk, "source": filename}
        for chunk in chunks_text
        if chunk.strip()  # ignora chunks vazios
    ]

    return chunks


def process_pdf(pdf_bytes: bytes, filename: str) -> list[dict]:
    """
    Pipeline completo: PDF bytes → lista de chunks prontos para indexação.

    Parâmetros:
        pdf_bytes: conteúdo do PDF em bytes
        filename: nome do arquivo

    Retorna:
        Lista de chunks com metadados
    """
    text = extract_text_from_pdf(pdf_bytes, filename)

    if not text.strip():
        raise ValueError(f"O PDF '{filename}' parece estar vazio ou ser uma imagem escaneada sem OCR.")

    chunks = split_into_chunks(text, filename)
    return chunks
