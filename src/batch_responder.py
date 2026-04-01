"""
src/batch_responder.py
----------------------
Responsável por processar um lote de perguntas em sequência,
aplicando RAG para cada uma e gerando respostas automáticas.

Orquestra o pipeline completo:
pergunta → busca semântica → prompt enriquecido → resposta.
"""
import time
from src.gemini_client import get_ai_response
from src.vector_store import search_similar_chunks
from src.config import SYSTEM_PROMPT, SYSTEM_PROMPT_RAG, TOP_K_CHUNKS

DELAY_ENTRE_PERGUNTAS = 15  # segundos entre cada chamada à API


def build_rag_prompt(pergunta, chunks):
    if not chunks:
        return SYSTEM_PROMPT
    context_text = "\n\n---\n\n".join([
        f"[Fonte: {chunk['source']}]\n{chunk['content']}"
        for chunk in chunks
    ])
    return SYSTEM_PROMPT_RAG.format(context=context_text)


def respond_single(pergunta, vector_store, categoria=""):
    query = f"{categoria}: {pergunta}" if categoria else pergunta

    if vector_store:
        chunks = search_similar_chunks(vector_store, query, k=TOP_K_CHUNKS)
        system_prompt = build_rag_prompt(pergunta, chunks)
    else:
        chunks = []
        system_prompt = SYSTEM_PROMPT

    resposta = get_ai_response(
        user_message=pergunta,
        history=[],
        system_prompt=system_prompt,
    )

    if "429" in resposta or "RESOURCE_EXHAUSTED" in resposta:
        return {
            "resposta": "⚠️ Cota da API atingida. Aguarde alguns minutos e processe o próximo lote.",
            "sources": chunks,
            "erro_cota": True,
        }

    return {"resposta": resposta, "sources": chunks, "erro_cota": False}


def respond_batch(perguntas, vector_store, progress_callback=None):
    resultados = []
    total = len(perguntas)

    for idx, item in enumerate(perguntas):
        if progress_callback:
            progress_callback(idx, total, item.get("num", str(idx + 1)))

        resultado = respond_single(
            pergunta=item["pergunta"],
            vector_store=vector_store,
            categoria=item.get("categoria", ""),
        )

        resultados.append({
            **item,
            "resposta": resultado["resposta"],
            "sources": resultado["sources"],
        })

        # Para imediatamente se a cota foi atingida
        if resultado.get("erro_cota"):
            break

        # Aguarda entre perguntas (exceto na última)
        if idx < total - 1:
            time.sleep(DELAY_ENTRE_PERGUNTAS)

    return resultados