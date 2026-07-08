# 🌿 Eco Lifestyle Agent

> **AI-powered sustainability guide** — built with IBM Granite, watsonx.ai, RAG, LangChain, ChromaDB, FastAPI, and Streamlit.

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://python.org)
[![IBM Granite](https://img.shields.io/badge/IBM-Granite%2013B-0f62fe)](https://www.ibm.com/watsonx)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.35-ff4b4b)](https://streamlit.io)
[![ChromaDB](https://img.shields.io/badge/ChromaDB-0.5-orange)](https://www.trychroma.com)

---

## 📋 Table of Contents

1. [Features](#features)
2. [Architecture](#architecture)
3. [Project Structure](#project-structure)
4. [Prerequisites](#prerequisites)
5. [Local Setup](#local-setup)
6. [IBM Cloud Setup](#ibm-cloud-setup)
7. [Running the Application](#running-the-application)
8. [Customising the Agent](#customising-the-agent)
9. [API Reference](#api-reference)
10. [Deployment](#deployment)
11. [Contributing](#contributing)

---

## ✨ Features

| Feature | Description |
|---|---|
| 💬 **AI Eco Chatbot** | Natural language Q&A powered by IBM Granite 13B Chat |
| 🔍 **RAG Pipeline** | Retrieves from curated environmental knowledge base |
| 📊 **Eco Dashboard** | Visual sustainability metrics and carbon context |
| 🧮 **Carbon Calculator** | Household footprint with India-specific emission factors |
| 🏆 **Eco Score Tracker** | Graded sustainability rating with improvement milestones |
| 🏛️ **Govt. Schemes** | Central & state environmental incentives for India 2024 |
| ♻️ **Recycling Guide** | Waste segregation, composting, and e-waste disposal |
| 🛒 **Eco Products** | Room-by-room sustainable product alternatives |
| 📄 **PDF Ingestion** | Upload documents to expand the knowledge base |
| 🌙 **Dark/Light Mode** | Toggle between themes |
| 👤 **User Preferences** | Personalised responses based on location, lifestyle, diet |
| 📝 **Feedback System** | Star-rating for AI responses |

---

## 🏗️ Architecture

```
User Browser
     │
     ▼
┌─────────────────────────────────────┐
│  Streamlit Frontend (frontend/app.py)│
│  - Chat UI, Dashboard, Calculator   │
│  - Dark/Light theme, Responsive     │
└────────────────┬────────────────────┘
                 │ HTTP (REST)
                 ▼
┌─────────────────────────────────────┐
│   FastAPI Backend (backend/main.py)  │
│   - /api/v1/chat                    │
│   - /api/v1/carbon/calculate        │
│   - /api/v1/documents/upload        │
└────────────────┬────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────┐
│    RAG Pipeline (rag/pipeline.py)   │
│  ┌──────────────┐  ┌─────────────┐ │
│  │  EcoRetriever│  │  GraniteLLM │ │
│  │  (Semantic   │  │  (IBM       │ │
│  │   Search)    │  │  watsonx.ai)│ │
│  └──────┬───────┘  └─────────────┘ │
└─────────┼───────────────────────────┘
          │
          ▼
┌─────────────────────────────────────┐
│  ChromaDB Vector Store              │
│  (vectordb/chroma_store/)           │
│  - IBM Slate / MiniLM Embeddings    │
│  - 20+ eco knowledge documents      │
│  - PDF upload support               │
└─────────────────────────────────────┘
```

---

## 📁 Project Structure

```
eco_lifestyle_agent/
│
├── frontend/                 # Streamlit UI
│   ├── app.py                # Main app — all pages
│   ├── styles.py             # CSS themes (light/dark)
│   ├── components.py         # Reusable UI components
│   └── __init__.py
│
├── backend/                  # FastAPI REST API
│   ├── main.py               # All routes
│   └── __init__.py
│
├── rag/                      # RAG pipeline
│   ├── embeddings.py         # IBM Slate / local embedding wrapper
│   ├── vector_store.py       # ChromaDB management
│   ├── retriever.py          # Semantic search & context formatting
│   ├── llm.py                # IBM Granite LLM wrapper
│   ├── pipeline.py           # End-to-end RAG orchestration
│   └── __init__.py
│
├── vectordb/                 # Vector database storage
│   └── chroma_store/         # ChromaDB persistent files
│
├── prompts/                  # Agent instructions (EDIT THIS)
│   ├── agent_instructions.py # Tone, style, safety, tips, factors
│   └── __init__.py
│
├── config/                   # Application configuration
│   ├── settings.py           # Pydantic settings from .env
│   └── __init__.py
│
├── datasets/                 # Knowledge base sources
│   ├── eco_knowledge_base.json  # 20 curated eco documents
│   └── uploads/              # User-uploaded PDFs/TXTs
│
├── scripts/                  # Utility scripts
│   ├── ingest_documents.py   # Load data into ChromaDB
│   └── __init__.py
│
├── utils/                    # Shared helpers
│   ├── helpers.py            # Carbon calc, tips, text utils
│   ├── logger.py             # Loguru logging
│   └── __init__.py
│
├── logs/                     # Application logs
├── .env.example              # Environment variable template
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

---

## 🔧 Prerequisites

| Requirement | Version | Notes |
|---|---|---|
| Python | 3.10+ | 3.11 recommended |
| pip | latest | `pip install --upgrade pip` |
| IBM Cloud Account | Free Lite | For Granite & Slate models |
| watsonx.ai Project | Required | Create at cloud.ibm.com |

---

## 💻 Local Setup

### 1. Clone / navigate to project

```bash
cd eco_lifestyle_agent
```

### 2. Create virtual environment

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

> 💡 **No IBM account yet?** The app still works with the local embedding fallback
> (sentence-transformers) and a stub LLM. Add credentials later to enable full AI.

### 4. Configure environment

```bash
cp .env.example .env
# Edit .env with your IBM credentials
```

Minimum required in `.env`:
```env
IBM_API_KEY=your_ibm_cloud_api_key
IBM_PROJECT_ID=your_watsonx_project_id
```

### 5. Ingest the knowledge base

```bash
python scripts/ingest_documents.py
```

This embeds all documents in `datasets/` into ChromaDB. Takes ~1–3 minutes.

### 6. Start the backend

```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

### 7. Start the frontend (new terminal)

```bash
streamlit run frontend/app.py
```

Open **http://localhost:8501** in your browser.

---

## ☁️ IBM Cloud Setup

### Step 1: Create an IBM Cloud Account
1. Go to https://cloud.ibm.com/registration
2. Select the **Lite (Free)** plan
3. Verify your email

### Step 2: Create a watsonx.ai Project
1. Navigate to https://dataplatform.cloud.ibm.com
2. Click **New Project → Create an empty project**
3. Note the **Project ID** from the project settings

### Step 3: Get your API Key
1. Go to https://cloud.ibm.com/iam/apikeys
2. Click **Create → IBM Cloud API key**
3. Copy the key immediately (shown only once)

### Step 4: Verify Model Access
1. In watsonx.ai, go to **Foundation Models**
2. Confirm you have access to:
   - `ibm/granite-13b-chat-v2` (LLM)
   - `ibm/slate-125m-english-rtrvr` (Embeddings)

### Step 5: Update `.env`
```env
IBM_API_KEY=your_actual_api_key
IBM_WATSONX_URL=https://us-south.ml.cloud.ibm.com
IBM_PROJECT_ID=your_actual_project_id
GRANITE_LLM_MODEL=ibm/granite-13b-chat-v2
GRANITE_EMBED_MODEL=ibm/slate-125m-english-rtrvr
```

---

## 🚀 Running the Application

### Option A: Full Stack (Recommended)

```bash
# Terminal 1 — Backend
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2 — Frontend
streamlit run frontend/app.py
```

### Option B: Frontend Only (no backend process needed)

The Streamlit frontend automatically falls back to direct RAG pipeline calls
when the backend is unreachable. Perfect for development/demo:

```bash
streamlit run frontend/app.py
```

### Option C: Re-ingest with custom PDF

```bash
python scripts/ingest_documents.py --source pdf --path datasets/my_report.pdf
```

### Option D: Reset and re-ingest everything

```bash
python scripts/ingest_documents.py --reset
```

---

## 🎛️ Customising the Agent

All agent behaviour is controlled in **`prompts/agent_instructions.py`**:

```python
# Change response tone
RESPONSE_TONE = "friendly"  # "professional", "academic", "motivational"

# Change verbosity
RESPONSE_LENGTH = "balanced"  # "concise", "detailed"

# Focus on specific topics
TOPIC_WEIGHTS = {
    "government_schemes": 1.0,  # Increase weight
    "biodiversity": 0.3,        # Decrease weight
}

# Modify safety guidelines
SAFETY_GUIDELINES = """
Your custom safety rules here...
"""

# Add/edit daily tips
DAILY_ECO_TIPS.append("🌿 Your custom tip here")

# Change citation format
CITATION_FORMAT = "footnote"  # "inline", "none"

# Update emission factors
CARBON_EMISSION_FACTORS["electricity_india"] = 0.82  # Updated CEA factor
```

No other files need to change when adjusting agent personality.

---

## 📡 API Reference

| Endpoint | Method | Description |
|---|---|---|
| `GET /api/health` | GET | Health check |
| `POST /api/v1/chat` | POST | Main chat (RAG + Granite) |
| `POST /api/v1/chat/stream` | POST | Streaming chat (SSE) |
| `GET /api/v1/tip/daily` | GET | Today's eco tip |
| `GET /api/v1/tip/random` | GET | Random eco tip |
| `POST /api/v1/carbon/calculate` | POST | Carbon footprint calculation |
| `POST /api/v1/documents/upload` | POST | Upload PDF/TXT to KB |
| `POST /api/v1/feedback` | POST | Submit response rating |
| `GET /api/v1/categories` | GET | List KB categories |

Interactive docs: **http://localhost:8000/api/docs**

### Example chat request:

```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "question": "How can I reduce plastic waste at home?",
    "user_preferences": {
      "location": "Mumbai",
      "lifestyle": "Urban Apartment",
      "transport": "Public Transit"
    }
  }'
```

---

## 🌐 Deployment

### IBM Cloud (Code Engine)

```bash
# Build container
docker build -t eco-lifestyle-agent .

# Push to IBM Container Registry
ibmcloud cr login
docker tag eco-lifestyle-agent us.icr.io/YOUR_NAMESPACE/eco-agent:latest
docker push us.icr.io/YOUR_NAMESPACE/eco-agent:latest

# Deploy to Code Engine
ibmcloud ce application create \
  --name eco-lifestyle-agent \
  --image us.icr.io/YOUR_NAMESPACE/eco-agent:latest \
  --port 8501 \
  --env-from-secret eco-agent-secrets
```

### Streamlit Community Cloud (Free)

1. Push code to GitHub (exclude `.env`)
2. Go to https://share.streamlit.io
3. Connect repository → select `frontend/app.py`
4. Add IBM credentials in **Secrets** section

### Docker Compose

```yaml
# docker-compose.yml (create in project root)
version: '3.8'
services:
  backend:
    build: .
    command: uvicorn backend.main:app --host 0.0.0.0 --port 8000
    env_file: .env
    ports: ["8000:8000"]
  frontend:
    build: .
    command: streamlit run frontend/app.py --server.port 8501
    env_file: .env
    ports: ["8501:8501"]
    depends_on: [backend]
```

---

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Test specific module
pytest tests/test_rag.py -v
```

---

## 📊 Knowledge Base Topics

The default knowledge base covers 20 curated documents across:

- **Waste Management** — 5Rs, plastic reduction, segregation guide
- **Water Conservation** — 20 home techniques, rainwater harvesting
- **Energy** — Solar, wind, biogas, efficiency tips
- **Transport** — Carbon comparisons, EVs, FAME II scheme
- **Food** — Plant-based diets, food waste, carbon of foods
- **Government Schemes** — PM Surya Ghar, FAME II, NCAP, Jal Jeevan Mission
- **Recycling** — E-waste, composting (aerobic, vermicomposting, bokashi)
- **Products** — Room-by-room eco alternatives, Indian brands
- **Carbon Footprint** — Calculation guide, India emission factors
- **Biodiversity** — Urban gardening, native plants, pollinators
- **Air Quality** — Indoor/outdoor, AQI guide, purifying plants
- **Climate Change** — Science, India impacts, NDC commitments

---

## 📄 License

MIT License — free to use, modify, and distribute.

---

## 🙏 Acknowledgements

- **IBM watsonx.ai** — Granite foundation models & Slate embeddings
- **LangChain** — RAG framework abstractions
- **ChromaDB** — Vector database
- **Streamlit** — Rapid UI development
- **FastAPI** — Modern Python API framework
- **UNEP, IPCC, MoEFCC, CEA** — Environmental data sources

---

*Built for sustainability hackathons and real-world deployment.  
Every query answered is a step toward a greener planet. 🌍*
