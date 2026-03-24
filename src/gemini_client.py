"""
src/gemini_client.py
--------------------
Responsável por toda comunicação com a API do Google Gemini.
Isolado aqui para que, no futuro, seja fácil trocar de modelo
sem mexer no restante do código.
"""

import os
from google import genai
import streamlit as st


def get_ai_response(user_message: str, history: list, system_prompt: str) -> str:

    api_key = st.secrets.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")

    if not api_key:
        st.error("❌ GEMINI_API_KEY não encontrada.")
        st.stop()

    client = genai.Client(api_key=api_key)

    contents = []
    for msg in history:
        role = "user" if msg["role"] == "user" else "model"
        contents.append({"role": role, "parts": [{"text": msg["content"]}]})

    contents.append({
        "role": "user",
        "parts": [{"text": f"{system_prompt}\n\n---\n\nPergunta: {user_message}"}]
    })

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=contents,
        )
        return response.text
    except Exception as e:
        return f"⚠️ Erro ao contatar a API do Gemini: {str(e)}"