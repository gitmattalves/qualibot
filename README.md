# 🏭 QualiBot — Assistente de Questionários de Qualificação Industrial

Sistema de IA para resposta automatizada de questionários de qualificação de fornecedores industriais, com base em documentos técnicos e normas de qualidade.

> Projeto de portfólio desenvolvido para demonstrar habilidades em IA aplicada,
> RAG (Retrieval-Augmented Generation) e automação de processos corporativos.

---

## 🗺️ Módulos do Projeto

| Módulo | Descrição | Status |
|--------|-----------|--------|
| **1 — Chatbot base** | Interface web + integração com Gemini | ✅ Concluído |
| 2 — Base de conhecimento | Upload de PDFs + busca semântica (RAG) | 🔜 Em breve |
| 3 — Parser de questionários | Leitura automática de formulários | 🔜 Em breve |
| 4 — Revisão e exportação | Interface de aprovação + export Excel/PDF | 🔜 Em breve |

---

## 🚀 Como rodar localmente

### 1. Clone o repositório
```bash
git clone https://github.com/seu-usuario/qualibot.git
cd qualibot
```

### 2. Crie e ative o ambiente virtual
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### 3. Instale as dependências
```bash
pip install -r requirements.txt
```

### 4. Configure sua API Key do Gemini
- Acesse [Google AI Studio](https://aistudio.google.com/app/apikey)
- Crie uma API Key gratuita
- Edite o arquivo `.streamlit/secrets.toml`:
```toml
GEMINI_API_KEY = "sua_chave_aqui"
```

### 5. Execute a aplicação
```bash
streamlit run app.py
```

Acesse `http://localhost:8501` no navegador.

---

## 🏗️ Estrutura do Projeto

```
qualibot/
├── app.py                  # Aplicação principal (Streamlit)
├── requirements.txt        # Dependências Python
├── .gitignore
├── .streamlit/
│   └── secrets.toml        # API Keys (não vai pro GitHub)
└── src/
    ├── __init__.py
    ├── config.py           # System prompt e configurações
    └── gemini_client.py    # Comunicação com a API do Gemini
```

---

## 🛠️ Stack Tecnológica

- **Python 3.11+**
- **Streamlit** — interface web
- **Google Gemini 1.5 Flash** — modelo de linguagem
- **google-generativeai** — SDK oficial do Gemini

---

## 📋 Exemplos de Perguntas

O assistente responde perguntas como:

- *"A empresa possui certificação ISO 9001? Qual é a validade?"*
- *"Quais são os procedimentos de controle de qualidade utilizados no processo produtivo?"*
- *"A empresa possui política de sustentabilidade e metas de redução de CO₂?"*
- *"Descreva o processo de qualificação de fornecedores da empresa."*
- *"A empresa realiza auditorias internas de segurança? Com qual frequência?"*

---

## 📄 Licença

MIT License — livre para uso e adaptação.
