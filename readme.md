## IFRS 17 QA Bot

An AI-powered chatbot for actuaries and finance professionals to explore and understand the **IFRS 17 Insurance Contracts** standard.

Built with [Streamlit](https://streamlit.io) and [Embedchain](https://embedchain.ai), powered by Mistral-7B via Hugging Face.

---

### Features

- **IFRS 17 focused** – Answers questions on GMM, PAA, VFA measurement models, CSM, risk adjustment, discount rates, transition approaches, and disclosures
- **Expandable knowledge base** – Add PDFs or web pages at runtime using `/add <url>`
- **Conversational memory** – Maintains context across the chat session
- **Vector search** – Uses `sentence-transformers/all-mpnet-base-v2` to retrieve relevant excerpts before generating answers

---

### Getting Started

#### Prerequisites

- Python 3.8+
- A [Hugging Face access token](https://huggingface.co/settings/tokens) with inference access to `mistralai/Mistral-7B-Instruct-v0.2`

#### Installation

```bash
pip install -r requirements.txt
```

#### Run the app

```bash
streamlit run app.py
```

Enter your Hugging Face token in the sidebar, then start asking questions.

---

### Adding Knowledge Sources

Use the `/add` command in the chat to load IFRS 17 documents into the knowledge base:

```
/add https://www.ifrs.org/issued-standards/list-of-standards/ifrs-17-insurance-contracts/
```

Supported source types include web pages and PDF URLs.

---

### Configuration

Edit `config.yaml` to adjust model settings:

| Setting | Default | Description |
|---|---|---|
| `model` | `mistralai/Mistral-7B-Instruct-v0.2` | HuggingFace model ID |
| `temperature` | `0.1` | Lower = more deterministic answers |
| `max_tokens` | `500` | Max response length |
| `system_prompt` | IFRS 17 expert persona | Guides model behaviour |

---

### Tech Stack

| Component | Technology |
|---|---|
| UI | Streamlit |
| LLM | Mistral-7B-Instruct via HuggingFace |
| Embeddings | sentence-transformers/all-mpnet-base-v2 |
| Vector DB / RAG | Embedchain (ChromaDB) |
