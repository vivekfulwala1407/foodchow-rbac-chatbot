# FoodChow RBAC AI Chatbot

A RAG-based Role-Based Access Control AI chatbot for FoodChow Technologies.
Built with FastAPI, Next.js, ChromaDB, and Groq LLM.

## Tech Stack
- **Frontend**: Next.js 14, TypeScript, Tailwind CSS
- **Backend**: FastAPI, Python 3.12
- **LLM**: Groq API (llama-3.3-70b-versatile)
- **Vector DB**: ChromaDB
- **Embeddings**: sentence-transformers (all-MiniLM-L6-v2)
- **Auth**: JWT tokens

## Roles
| Role | Access |
|------|--------|
| C-Level | All departments |
| Finance | Finance + General |
| Marketing | Marketing + General |
| HR | HR + General |
| Engineering | Engineering + General |
| Employee | General only |

## Setup

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python ingestion/ingest.py  # Run once to load documents
python -m uvicorn app.main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## Environment Variables

### Backend `.env`
```
GROQ_API_KEY=your_key_here
JWT_SECRET_KEY=your_secret_here
JWT_ALGORITHM=HS256
JWT_EXPIRE_HOURS=8
CHROMA_DB_PATH=./chroma_db
CHROMA_COLLECTION_NAME=foodchow_docs
EMBEDDING_MODEL=all-MiniLM-L6-v2
LLM_MODEL=llama-3.3-70b-versatile
TOP_K_RESULTS=5
CHUNK_SIZE=800
CHUNK_OVERLAP=150
```

### Frontend `.env.local`
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```