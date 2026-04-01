# 🏭 QualiBot — Assistente IA para Questionários de Qualificação Industrial

![Python](https://img.shields.io/badge/Python-3.12+-3776AB?style=flat&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.35+-FF4B4B?style=flat&logo=streamlit&logoColor=white)
![Google Gemini](https://img.shields.io/badge/Google%20Gemini-2.5%20Flash-4285F4?style=flat&logo=google&logoColor=white)
![LangChain](https://img.shields.io/badge/LangChain-0.2+-1C3C3C?style=flat)
![FAISS](https://img.shields.io/badge/FAISS-Vector%20Store-0467DF?style=flat)
![Status](https://img.shields.io/badge/Status-Em%20desenvolvimento-yellow?style=flat)

> Sistema de inteligência artificial para resposta automatizada a questionários de qualificação de fornecedores industriais, com base em documentos técnicos da empresa.

---

## 📋 Sobre o Projeto

Empresas industriais recebem questionários de qualificação de clientes internacionais com dezenas de perguntas técnicas sobre qualidade, segurança, meio ambiente e ESG. Responder esses questionários manualmente consome horas de trabalho de especialistas.

O **QualiBot** automatiza esse processo utilizando **RAG (Retrieval-Augmented Generation)** — técnica que permite à IA responder com base nos documentos reais da empresa, citando a fonte de cada informação.

### Comparativo: antes e depois

| | Sem QualiBot | Com QualiBot |
|---|---|---|
| **Tempo de resposta** | Horas por questionário | Minutos |
| **Base de informação** | Conhecimento geral do analista | Documentos oficiais da empresa |
| **Rastreabilidade** | Nenhuma | Fonte citada em cada resposta |
| **Consistência** | Varia por analista | Padronizada |

---

## 🗺️ Roadmap

| Módulo | Descrição | Status |
|--------|-----------|--------|
| **1 — Chatbot base** | Interface web + integração com Google Gemini | ✅ Concluído |
| **2 — Base de conhecimento** | Upload de PDFs + busca semântica RAG | ✅ Concluído |
| **3 — Questionário automático** | Parser de Excel + respostas em lote com RAG | ✅ Concluído |
| 4 — Revisão e exportação avançada | Aprovação humana + exportação formatada | 📋 Planejado |

---

## ✨ Funcionalidades atuais

- 💬 **Chat especializado** em qualidade industrial com contexto técnico (ISO 9001, ISO 14001, FMEA, CEP, PPAP)
- 📄 **Upload de múltiplos PDFs** — manuais, políticas, certificações, procedimentos
- 🔍 **Busca semântica** — encontra respostas por significado, não por palavras-chave exatas
- 📋 **Processamento automático de questionários** — faz upload do Excel do cliente e o bot responde todas as perguntas automaticamente
- ⚙️ **Processamento em lotes** — controle de quantas perguntas processar por vez, respeitando os limites da API
- 📎 **Citação de fontes** — cada resposta indica o documento e o trecho utilizado
- ✏️ **Revisão humana** — edite as respostas geradas antes de exportar
- ⬇️ **Exportação do Excel preenchido** — arquivo pronto para enviar ao cliente
- 🛡️ **Reconhece limitações** — informa quando a resposta não está nos documentos carregados

---

## 🛠️ Stack Tecnológica

| Tecnologia | Uso |
|-----------|-----|
| **Python 3.12+** | Linguagem principal |
| **Streamlit** | Interface web |
| **Google Gemini 2.5 Flash** | Modelo de linguagem (LLM) |
| **google-genai SDK** | Integração com API do Gemini |
| **LangChain** | Orquestração do pipeline RAG |
| **FAISS** | Banco vetorial para busca semântica |
| **Gemini Embeddings** | Conversão de texto em vetores |
| **PyMuPDF** | Extração de texto de PDFs |
| **openpyxl** | Leitura e escrita de arquivos Excel |

---

## 🚀 Como rodar localmente

### Pré-requisitos
- Python 3.12+ instalado ([python.org](https://python.org/downloads))
- Conta Google com acesso ao [Google AI Studio](https://aistudio.google.com)

### Instalação

```bash
# 1. Clone o repositório
git clone https://github.com/gitmattalves/qualibot.git
cd qualibot

# 2. Crie e ative o ambiente virtual
python -m venv venv
venv\Scripts\activate       # Windows
# source venv/bin/activate  # Mac/Linux

# 3. Instale as dependências
pip install -r requirements.txt
```

### Configuração da API Key

1. Acesse [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)
2. Crie uma API Key gratuita
3. Edite o arquivo `.streamlit/secrets.toml`:

```toml
GEMINI_API_KEY = "sua_chave_aqui"
```

### Execução

```bash
streamlit run app.py --server.headless true
```

Acesse `http://localhost:8501` no navegador.

---

## 📁 Estrutura do Projeto

```
qualibot/
├── app.py                          # Aplicação principal (Streamlit)
├── requirements.txt                # Dependências Python
├── .gitignore
├── README.md
├── .streamlit/
│   └── secrets.toml                # API Keys (não vai ao GitHub)
└── src/
    ├── __init__.py
    ├── config.py                   # System prompts e configurações
    ├── gemini_client.py            # Comunicação com API do Gemini
    ├── document_loader.py          # Leitura e chunking de PDFs
    ├── vector_store.py             # Embeddings e busca semântica (FAISS)
    ├── questionnaire_parser.py     # Leitura e exportação de questionários Excel
    └── batch_responder.py          # Processamento em lote com RAG
```

---

## 💡 Como usar

### Modo chat livre
Faça perguntas diretamente sobre qualidade industrial, normas ISO, FMEA, CEP e ESG na aba **"Chat livre"**.

### Modo questionário automático
1. Na coluna esquerda, faça upload dos PDFs da empresa (manuais, políticas, certificações)
2. Na aba **"Questionário automático"**, faça upload do Excel com as perguntas do cliente
3. Escolha quantas perguntas processar por lote (recomendado: 5 para a cota gratuita)
4. Clique em **"Processar próximas X perguntas"**
5. Revise e edite as respostas geradas
6. Baixe o Excel preenchido com o botão de exportação

### Exemplos de perguntas respondidas automaticamente
```
"Qual é o número do certificado ISO 9001 e quando vence?"
→ Número: BV-SGQ-2024-BR-00847 · Validade: 22/03/2027
  Fonte: Manual_Qualidade_ISO9001.pdf

"Qual foi o PPM externo alcançado em 2024?"
→ 23 PPM (meta: < 50 PPM)
  Fonte: Manual_Qualidade_ISO9001.pdf

"Qual o índice de reciclagem de resíduos atingido?"
→ 88,4% (meta: > 85%)
  Fonte: Politica_Ambiental_ISO14001.pdf
```

---

## 🧠 Como funciona o RAG

```
PDFs → Extração de texto → Chunks (800 chars) → Embeddings → FAISS
                                                                  ↓
Excel → Parser → Perguntas → Embedding da pergunta → Top 3 chunks
                                                                  ↓
                              Chunks + Pergunta → Gemini → Resposta com fonte
                                                                  ↓
                                             Revisão humana → Excel exportado
```

---

## ⚠️ Observações

- O arquivo `.streamlit/secrets.toml` **nunca deve ser commitado** — já está no `.gitignore`
- O banco vetorial FAISS é armazenado **em memória** — é recriado a cada sessão
- A camada gratuita do Gemini suporta ~50 requisições/dia — use lotes de 5 perguntas
- PDFs escaneados sem OCR não são suportados nesta versão
- Compatível com Python 3.12. Python 3.14 funciona com aviso de compatibilidade do Pydantic

---

## 👤 Autor

**Mateus Alves**
Analista de Dados | BI & Automação | IA Aplicada

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Mateus%20Alves-0077B5?style=flat&logo=linkedin)](https://www.linkedin.com/in/mateus-alves-92ab9784/)
[![GitHub](https://img.shields.io/badge/GitHub-gitmattalves-181717?style=flat&logo=github)](https://github.com/gitmattalves)

---

## 📄 Licença

MIT License — livre para uso e adaptação.
