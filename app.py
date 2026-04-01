import streamlit as st
import time
from src.gemini_client import get_ai_response
from src.config import SYSTEM_PROMPT, SYSTEM_PROMPT_RAG, TOP_K_CHUNKS
from src.document_loader import process_pdf
from src.vector_store import build_vector_store, search_similar_chunks, add_documents_to_store
from src.questionnaire_parser import parse_questionnaire, export_answers_to_excel
from src.batch_responder import respond_batch

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
.q-card {
    background-color: #1a1f2e;
    border-radius: 8px;
    padding: 12px 16px;
    margin-bottom: 10px;
    border-left: 4px solid #00d4aa;
}
</style>
""", unsafe_allow_html=True)

col_sidebar, col_main = st.columns([1, 2.5], gap="large")

# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR — Documentos
# ══════════════════════════════════════════════════════════════════════════════
with col_sidebar:
    st.markdown('<p class="main-title">🏭 QualiBot</p>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Módulo 3 — Resposta automática de questionários</p>', unsafe_allow_html=True)
    st.divider()
    st.subheader("📄 Base de conhecimento")

    uploaded_pdfs = st.file_uploader(
        "Adicione PDFs",
        type=["pdf"],
        accept_multiple_files=True,
        help="Manuais, políticas, certificações..."
    )

    if uploaded_pdfs:
        if "processed_files" not in st.session_state:
            st.session_state.processed_files = set()
        for file in uploaded_pdfs:
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
                        st.success(f"✅ {file.name} ({len(chunks)} trechos)")
                    except Exception as e:
                        st.error(f"❌ {file.name}: {str(e)}")

    if "doc_list" in st.session_state and st.session_state.doc_list:
        st.divider()
        st.caption("Documentos indexados:")
        for doc in st.session_state.doc_list:
            st.markdown(f"📎 **{doc['name']}** · {doc['chunks']} trechos")
    else:
        st.info("Nenhum documento carregado.\nO bot responderá com conhecimento geral.")

    if "vector_store" in st.session_state:
        st.divider()
        if st.button("🗑️ Limpar base", use_container_width=True):
            for key in ["vector_store", "processed_files", "doc_list"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# MAIN — Tabs: Questionário | Chat
# ══════════════════════════════════════════════════════════════════════════════
with col_main:
    has_docs = "vector_store" in st.session_state
    if has_docs:
        st.success("🔍 Modo RAG ativo — respondendo com base nos seus documentos")
    else:
        st.info("💡 Modo geral — carregue PDFs para respostas específicas da empresa")

    tab_quest, tab_chat = st.tabs(["📋 Questionário automático", "💬 Chat livre"])

    # ── TAB 1: QUESTIONÁRIO ─────────────────────────────────────────────────
    with tab_quest:
        st.markdown("#### Upload do questionário")
        st.caption("Suba o Excel com as perguntas do cliente. O QualiBot responderá todas automaticamente.")

        quest_file = st.file_uploader(
            "Questionário Excel (.xlsx)",
            type=["xlsx"],
            key="quest_uploader"
        )

        if quest_file:
            quest_bytes = quest_file.read()

            # Parse das perguntas
            try:
                perguntas = parse_questionnaire(quest_bytes, quest_file.name)
                st.success(f"✅ {len(perguntas)} perguntas encontradas em **{quest_file.name}**")
            except Exception as e:
                st.error(f"❌ {str(e)}")
                perguntas = []

            if perguntas:
                # Preview das perguntas
                with st.expander(f"👁️ Preview — {len(perguntas)} perguntas identificadas", expanded=False):
                    for p in perguntas:
                        st.markdown(f"**{p['num']}.** [{p['categoria']}] {p['pergunta']}")

                col_btn1, col_btn2 = st.columns([1, 2])
                with col_btn1:
                    lote_size = st.selectbox(
                        "Perguntas por lote",
                        options=[3, 5, 10, 15],
                        index=1,
                        help="5 é o ideal para a cota gratuita do Gemini"
                    )

                # Calcula qual lote processar
                ja_respondidas = len([
                    p for p in perguntas
                    if p["num"] in {str(r["num"]) for r in st.session_state.get("resultados", [])}
                ])
                pendentes = perguntas[ja_respondidas:]
                proximo_lote = pendentes[:lote_size]

                if ja_respondidas > 0:
                    st.info(f"✅ {ja_respondidas} perguntas já respondidas · {len(pendentes)} pendentes")

                with col_btn1:
                    run_btn = st.button(
                        f"🚀 Processar próximas {len(proximo_lote)} perguntas",
                        use_container_width=True,
                        type="primary",
                        disabled=len(proximo_lote) == 0,
                    )

                if len(proximo_lote) == 0 and ja_respondidas > 0:
                    st.success("🎉 Todas as perguntas foram respondidas!")

                if run_btn:
                    st.divider()
                    st.markdown("#### Gerando respostas...")

                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    resultados_placeholder = st.empty()

                    resultados = []

                    def update_progress(idx, total, num):
                        pct = int((idx / total) * 100)
                        progress_bar.progress(pct)
                        status_text.caption(f"Processando pergunta {num} ({idx + 1}/{total})...")

                    if run_btn and proximo_lote:
                        st.divider()
                        st.markdown(f"#### Processando lote {ja_respondidas + 1}–{ja_respondidas + len(proximo_lote)}...")
                        st.caption(f"⏱️ Estimativa: ~{len(proximo_lote) * 15 // 60 + 1} minuto(s)")

                        progress_bar = st.progress(0)
                        status_text = st.empty()

                        def update_progress(idx, total, num):
                            pct = int((idx / total) * 100)
                            progress_bar.progress(pct)
                            status_text.caption(f"Processando pergunta {num} ({idx + 1}/{total})...")

                        novos = respond_batch(
                            perguntas=proximo_lote,
                            vector_store=st.session_state.get("vector_store"),
                            progress_callback=update_progress,
                        )

                        progress_bar.progress(100)

                        if "resultados" not in st.session_state:
                            st.session_state.resultados = []
                        st.session_state.resultados.extend(novos)
                        st.session_state.quest_bytes = quest_bytes

                        cota_atingida = any(
                            "Cota da API" in r.get("resposta", "") for r in novos
                        )
                        if cota_atingida:
                            st.warning("⚠️ Cota da API atingida. Aguarde alguns minutos e processe o próximo lote.")
                        else:
                            respondidas_agora = len([r for r in novos if "Cota" not in r.get("resposta", "")])
                            st.success(f"✅ {respondidas_agora} perguntas respondidas! Clique em 'Processar próximas' para continuar.")

                        st.rerun()

                    progress_bar.progress(100)
                    status_text.caption(f"✅ {len(resultados)} respostas geradas!")

                    st.session_state.resultados = resultados
                    st.session_state.quest_bytes = quest_bytes

                # Exibe resultados e permite edição
                if "resultados" in st.session_state:
                    st.divider()
                    st.markdown("#### Revisão das respostas")
                    st.caption("Edite as respostas antes de exportar. Clique em 'Fontes' para ver os trechos usados.")

                    respostas_editadas = []
                    for item in st.session_state.resultados:
                        with st.expander(f"**{item['num']}.** {item['pergunta']}", expanded=False):
                            st.caption(f"Categoria: {item['categoria']}")

                            resposta_editada = st.text_area(
                                "Resposta",
                                value=item["resposta"],
                                height=150,
                                key=f"resp_{item['row']}",
                                label_visibility="collapsed"
                            )

                            if item.get("sources"):
                                with st.expander("📎 Fontes consultadas", expanded=False):
                                    for s in item["sources"]:
                                        st.markdown(
                                            f'<div class="source-box"><strong>{s["source"]}</strong><br>'
                                            f'{s["content"][:250]}...</div>',
                                            unsafe_allow_html=True
                                        )

                            respostas_editadas.append({
                                "row": item["row"],
                                "resposta": resposta_editada,
                            })

                    st.divider()
                    st.markdown("#### Exportar")

                    excel_output = export_answers_to_excel(
                        st.session_state.quest_bytes,
                        respostas_editadas,
                    )

                    st.download_button(
                        label="⬇️ Baixar questionário respondido (.xlsx)",
                        data=excel_output,
                        file_name=f"QualiBot_Respondido_{quest_file.name}",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True,
                        type="primary",
                    )

    # ── TAB 2: CHAT ─────────────────────────────────────────────────────────
    with tab_chat:
        if "messages" not in st.session_state:
            st.session_state.messages = []
            st.session_state.messages.append({
                "role": "assistant",
                "content": "Olá! Sou o QualiBot. Use a aba 'Questionário automático' para processar um Excel completo, ou faça perguntas aqui no chat. Como posso ajudar?"
            })

        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
                if msg.get("sources"):
                    with st.expander("📎 Fontes consultadas", expanded=False):
                        for source in msg["sources"]:
                            st.markdown(
                                f'<div class="source-box"><strong>{source["source"]}</strong><br>'
                                f'{source["content"][:300]}{"..." if len(source["content"]) > 300 else ""}</div>',
                                unsafe_allow_html=True
                            )

        if prompt := st.chat_input("Digite sua pergunta..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                sources_used = []
                with st.spinner("Consultando base de conhecimento..."):
                    if has_docs:
                        chunks = search_similar_chunks(st.session_state.vector_store, prompt, k=TOP_K_CHUNKS)
                        sources_used = chunks
                        context_text = "\n\n---\n\n".join([
                            f"[Fonte: {c['source']}]\n{c['content']}" for c in chunks
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
                            st.markdown(
                                f'<div class="source-box"><strong>{source["source"]}</strong><br>'
                                f'{source["content"][:300]}{"..." if len(source["content"]) > 300 else ""}</div>',
                                unsafe_allow_html=True
                            )

            st.session_state.messages.append({
                "role": "assistant",
                "content": response,
                "sources": sources_used
            })

st.divider()
st.caption("QualiBot v3.0 · Módulo 3: Resposta automática de questionários · Powered by Google Gemini + FAISS")
