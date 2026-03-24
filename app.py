import streamlit as st
from src.gemini_client import get_ai_response
from src.config import SYSTEM_PROMPT, SYSTEM_PROMPT_RAG, TOP_K_CHUNKS
from src.document_loader import process_pdf
from src.vector_store import build_vector_store, search_similar_chunks, add_documents_to_store

st.set_page_config(page_title="QualiBot", page_icon="🏭", layout="wide")

st.markdown("""
<style>
.stApp { background-color: #0f1117; }
.main-title { font-size: 2rem; font-weight: 700; color: #00d4aa; margin-bottom: 0; }
.subtitle { color: #8b949e; font-size: 0.95rem; margin-bottom: 1rem; }
.source-box {
    background-color: #1a1f2e;
    border-left: 3px solid #00d4aa;
    padding: 8px 12px;
    border-radius: 0 6px 6px 0;
    margin-top: 8px;
    font-size: 0.82rem;
    color: #8b949e;
}
</style>
""", unsafe_allow_html=True)

col_sidebar, col_chat = st.columns([1, 2.5], gap="large")

with col_sidebar:
    st.markdown('<p class="main-title">🏭 QualiBot</p>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Módulo 2 — Base de conhecimento</p>', unsafe_allow_html=True)
    st.divider()
    st.subheader("📄 Documentos carregados")

    uploaded_files = st.file_uploader(
        "Adicione PDFs à base de conhecimento",
        type=["pdf"],
        accept_multiple_files=True,
        help="Manuais de qualidade, políticas, certificações, procedimentos..."
    )

    if uploaded_files:
        if "processed_files" not in st.session_state:
            st.session_state.processed_files = set()

        for file in uploaded_files:
            if file.name not in st.session_state.processed_files:
                with st.spinner(f"Indexando {file.name}..."):
                    try:
                        chunks = process_pdf(file.read(), file.name)
                        if "vector_store" not in st.session_state:
                            st.session_state.vector_store = build_vector_store(chunks)
                        else:
                            st.session_state.vector_store = add_documents_to_store(
                                st.session_state.vector_store, chunks
                            )
                        st.session_state.processed_files.add(file.name)
                        if "doc_list" not in st.session_state:
                            st.session_state.doc_list = []
                        st.session_state.doc_list.append({"name": file.name, "chunks": len(chunks)})
                        st.success(f"✅ {file.name} indexado ({len(chunks)} trechos)")
                    except Exception as e:
                        st.error(f"❌ Erro ao processar {file.name}: {str(e)}")

    if "doc_list" in st.session_state and st.session_state.doc_list:
        st.divider()
        st.caption("Base de conhecimento ativa:")
        for doc in st.session_state.doc_list:
            st.markdown(f"📎 **{doc['name']}** · {doc['chunks']} trechos")
    else:
        st.info("Nenhum documento carregado ainda.\nO bot responderá com conhecimento geral.")

    if "vector_store" in st.session_state:
        st.divider()
        if st.button("🗑️ Limpar base de conhecimento", use_container_width=True):
            for key in ["vector_store", "processed_files", "doc_list"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()

with col_chat:
    has_docs = "vector_store" in st.session_state
    if has_docs:
        st.success("🔍 Modo RAG ativo — respondendo com base nos seus documentos")
    else:
        st.info("💡 Modo geral — carregue PDFs para respostas específicas da empresa")

    if "messages" not in st.session_state:
        st.session_state.messages = []
        st.session_state.messages.append({
            "role": "assistant",
            "content": (
                "Olá! Sou o QualiBot. "
                "Você pode me fazer perguntas diretamente ou carregar documentos PDF "
                "na coluna ao lado para que eu responda com base neles. "
                "Como posso ajudar?"
            )
        })

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg.get("sources"):
                with st.expander("📎 Fontes consultadas", expanded=False):
                    for source in msg["sources"]:
                        st.markdown(f'<div class="source-box"><strong>{source["source"]}</strong><br>{source["content"][:300]}{"..." if len(source["content"]) > 300 else ""}</div>', unsafe_allow_html=True)

    if prompt := st.chat_input("Digite sua pergunta sobre qualificação industrial..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            sources_used = []
            with st.spinner("Consultando base de conhecimento..."):
                if has_docs:
                    relevant_chunks = search_similar_chunks(st.session_state.vector_store, prompt, k=TOP_K_CHUNKS)
                    sources_used = relevant_chunks
                    context_text = "\n\n---\n\n".join([
                        f"[Fonte: {chunk['source']}]\n{chunk['content']}"
                        for chunk in relevant_chunks
                    ])
                    system_prompt = SYSTEM_PROMPT_RAG.format(context=context_text)
                else:
                    system_prompt = SYSTEM_PROMPT

                response = get_ai_response(
                    user_message=prompt,
                    history=st.session_state.messages[:-1],
                    system_prompt=system_prompt,
                )

            st.markdown(response)

            if sources_used:
                with st.expander("📎 Fontes consultadas", expanded=False):
                    for source in sources_used:
                        st.markdown(f'<div class="source-box"><strong>{source["source"]}</strong><br>{source["content"][:300]}{"..." if len(source["content"]) > 300 else ""}</div>', unsafe_allow_html=True)

        st.session_state.messages.append({
            "role": "assistant",
            "content": response,
            "sources": sources_used
        })

st.divider()
st.caption("QualiBot v2.0 · Módulo 2: Base de conhecimento RAG · Powered by Google Gemini + FAISS")
