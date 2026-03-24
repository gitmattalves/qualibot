"""
src/vector_store.py
-------------------
Responsável por transformar chunks em vetores (embeddings)
e realizar buscas semânticas.

O que são embeddings?
São representações numéricas de textos. Textos com significado
parecido ficam "perto" no espaço vetorial, mesmo usando palavras
diferentes. Ex: "certificado ISO" e "norma de qualidade" ficam
próximos, mesmo sem compartilhar palavras.

O FAISS (Facebook AI Similarity Search) é o banco que armazena
esses vetores e permite buscar os mais próximos de forma eficiente.
"""

import os
import streamlit as st
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document


def _get_embeddings():
    """
    Inicializa o modelo de embeddings do Google Gemini.
    Usa a mesma API Key configurada no secrets.toml.
    """
    api_key = st.secrets.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")
    return GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001",
        google_api_key=api_key,
    )


def build_vector_store(chunks: list[dict]) -> FAISS:
    """
    Constrói o banco vetorial a partir dos chunks.

    Processo:
    1. Converte cada chunk em um objeto Document do LangChain
    2. Envia os textos para a API de embeddings do Gemini
    3. Armazena os vetores no FAISS (em memória)

    Parâmetros:
        chunks: lista de {'content': str, 'source': str}

    Retorna:
        Objeto FAISS pronto para buscas
    """
    documents = [
        Document(
            page_content=chunk["content"],
            metadata={"source": chunk["source"]}
        )
        for chunk in chunks
    ]

    embeddings = _get_embeddings()
    vector_store = FAISS.from_documents(documents, embeddings)
    return vector_store


def search_similar_chunks(
    vector_store: FAISS,
    query: str,
    k: int = 3
) -> list[dict]:
    """
    Busca os k chunks mais relevantes para a pergunta do usuário.

    A busca é semântica — não procura palavras exatas, mas significado.
    "Como a empresa controla qualidade?" vai encontrar chunks sobre
    FMEA, CEP, inspeção, mesmo que não contenham exatamente essa frase.

    Parâmetros:
        vector_store: banco FAISS já construído
        query: pergunta do usuário
        k: número de chunks a retornar (padrão: 3)

    Retorna:
        Lista de {'content': str, 'source': str}
    """
    results = vector_store.similarity_search(query, k=k)

    return [
        {
            "content": doc.page_content,
            "source": doc.metadata.get("source", "Documento desconhecido")
        }
        for doc in results
    ]


def add_documents_to_store(
    existing_store: FAISS,
    new_chunks: list[dict]
) -> FAISS:
    """
    Adiciona novos chunks a um banco vetorial já existente.
    Usado quando o usuário sobe um segundo PDF sem querer perder o primeiro.

    Parâmetros:
        existing_store: banco FAISS já existente
        new_chunks: novos chunks a adicionar

    Retorna:
        Banco FAISS atualizado
    """
    new_documents = [
        Document(
            page_content=chunk["content"],
            metadata={"source": chunk["source"]}
        )
        for chunk in new_chunks
    ]

    embeddings = _get_embeddings()
    new_store = FAISS.from_documents(new_documents, embeddings)
    existing_store.merge_from(new_store)
    return existing_store
