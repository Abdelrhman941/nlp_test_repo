# **🐾 Pet Health RAG Chatbot**

> **Production-ready RAG chatbot with FastAPI backend**

![Version](https://img.shields.io/badge/version-1.0.0-blue) ![Python](https://img.shields.io/badge/python-3.10+-green) ![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-teal) ![License](https://img.shields.io/badge/license-MIT-orange)

## **🎯 Overview**

A complete full-stack implementation of a Retrieval-Augmented Generation (RAG) chatbot specialized in pet health information. The system combines:

- **FastAPI Backend**: RESTful API with chat session management
- **Vanilla JS Frontend**: ChatGPT-inspired dark mode interface
- **RAG Pipeline**: FAISS vector search + Qwen2.5-3B-Instruct LLM
- **PetMD Knowledge Base**: 1000+ curated articles on pet health

## **Quick Start**

> ### do this direct:
```bash
./run.sh
```

### 1. Install Dependencies
```bash
pip install -r backend/requirements.txt
```

### 2. Start Backend
```bash
# Windows: Double-click start_backend.bat
# Or manually:
python -m backend.main
```

Backend runs at: **http://localhost:8000**

### 3. Open Frontend
```bash
# Windows: Double-click start_frontend.bat
# Or manually: Open frontend/index.html in browser
# Or use Python server:
cd frontend
python -m http.server 8080
```

### 4. Start Chatting! 🎉
Visit http://localhost:8080 (or just open `frontend/index.html`)

## **📂 Project Structure**
```
nlp-project/
├── backend/
│   ├── api/
│   │   └── routes.py          # API endpoints (POST /chat)
│   ├── models/
│   │   └── models.py          # Pydantic schemas
│   ├── utils/
│   │   └── helpers.py         # Business logic & ChatMemory
│   ├── config.py              # Configuration management
│   ├── main.py                # FastAPI application
│   └── .env                   # Environment variables
│
├── frontend/
│   ├── index.html             # UI structure
│   ├── style.css              # Dark mode styling
│   └── script.js              # Frontend logic & API calls
│
├── rag/
│   ├── model/
│   │   └──...
│   ├── chatbot.py             # Main RAG pipeline
│   ├── retriever.py           # FAISS vector search
│   ├── guards.py              # Input validation & safety
│   ├── eval.py                # Evaluation metrics
│   └── build_index.py         # Index builder
│
├── Data/
│   ├── petmd.index            # FAISS index (1000+ docs)
│   ├── documents_semantic.pkl # Embeddings
│   ├── articles_data.json     # Source articles
│   └── article_links.json     # Article URLs
│
├── article_scraper.py         # Article content scraper
├── sitemap_scraper.py         # Sitemap URL extractor
├── sitemap_scraper.py         # Sitemap URL extractor
├── evaluation.py              # Model evaluation
├── Arch.excalidraw            # just for drawing and add notes
├── .gitignore
├── README.md
└── requirements.txt
```

## **✨ Features**

### - Backend
- ✅ RESTful API with FastAPI
- ✅ Chat session management (in-memory)
- ✅ Pydantic request/response validation
- ✅ CORS enabled for frontend integration
- ✅ Automatic API documentation (Swagger UI)
- ✅ Health check endpoint
- ✅ Environment-based configuration
- ✅ Clean modular architecture

### - Frontend
- ✅ ChatGPT-inspired dark mode UI (#121212)
- ✅ Sidebar with chat history
- ✅ Create/rename/delete chats
- ✅ Real-time messaging with loading states
- ✅ Smooth animations and transitions
- ✅ Auto-scroll to latest messages
- ✅ Source citation display
- ✅ LocalStorage persistence
- ✅ Keyboard shortcuts (Enter to send)
- ✅ Responsive design

### - RAG Features
- ✅ FAISS vector similarity search
- ✅ Semantic retrieval (top-K chunks)
- ✅ Context-aware responses
- ✅ Emergency detection
- ✅ Language validation
- ✅ Greeting/farewell handling

> [!NOTE]
> *This is the end, Thanks for reading. 😁*
