# FoodChow RBAC AI Chatbot

A sophisticated Role-Based Access Control (RBAC) AI chatbot built with FastAPI, Next.js, PostgreSQL, ChromaDB, and Groq LLM. This application provides intelligent document retrieval and querying across multiple departments with fine-grained access control.

## 📖 Full Documentation

For comprehensive setup instructions, API documentation, and troubleshooting, see [README_COMPLETE.md](README_COMPLETE.md) which includes detailed guides for both **macOS and Windows**.

[👉 Read Full Documentation](README_COMPLETE.md)

---

## 🎯 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 18+
- PostgreSQL 12+
- Groq API Key ([get one free here](https://console.groq.com))

### ⚡ 30-Second Setup (macOS)

```bash
# 1. Clone and setup backend
cd backend && python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt

# 2. Create .env file
cat > .env << EOF
DATABASE_URL=postgresql://foodchow_user:password@localhost:5432/foodchow_db
GROQ_API_KEY=your_key_here
JWT_SECRET_KEY=super_secret_key
CHROMA_DB_PATH=./chroma_db
CHROMA_COLLECTION_NAME=foodchow_docs
EMBEDDING_MODEL=all-MiniLM-L6-v2
LLM_MODEL=llama-3.3-70b-versatile
EOF

# 3. Initialize DB and ingest documents
python ingestion/ingest.py

# 4. Start backend
python -m uvicorn app.main:app --reload --port 8000
```

**In another terminal:**

```bash
# 5. Setup frontend
cd frontend && npm install && echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local && npm run dev
```

Open **http://localhost:3000** ✨

---

## 📚 Tech Stack

| Category | Technology |
|----------|-----------|
| **Frontend** | Next.js 16, React 19, TypeScript, Tailwind CSS |
| **Backend** | FastAPI, Python 3.8+, SQLAlchemy |
| **Database** | PostgreSQL 12+, ChromaDB 0.4.24 |
| **AI/ML** | Groq LLM (llama-3.3-70b), Sentence Transformers |
| **Auth** | JWT (PyJWT), bcrypt |
| **State** | Zustand (Frontend) |

---

## 🔐 Role-Based Access Control

| Role | Departments | Use Case |
|------|----------|----------|
| **C-Level** | All | Executive access to all organizational data |
| **Finance** | Finance + General | Finance and company-wide documents |
| **Marketing** | Marketing + General | Marketing and company-wide documents |
| **HR** | HR + General | HR and company-wide documents |
| **Engineering** | Engineering + General | Engineering and company-wide documents |
| **Employee** | General only | Access to public/general documents only |

**Default Test Users:**
```
admin / admin123 (C-Level)
finance_user / finance123 (Finance)
hr_user / hr123 (HR)
marketing_user / marketing123 (Marketing)
eng_user / eng123 (Engineering)
employee / employee123 (Employee)
```

⚠️ Change these in production!

---

## 🗂️ Project Structure

```
backend/                    # FastAPI application
├── app/
│   ├── auth/              # JWT authentication
│   ├── chat/              # RAG chat endpoints
│   ├── rag/               # RAG pipeline
│   ├── rbac/              # Access control
│   ├── database/          # PostgreSQL + SQLAlchemy
│   └── admin/             # User management
├── ingestion/             # Document ingestion
├── data/                  # Source documents
├── chroma_db/             # Vector store
└── requirements.txt

frontend/                   # Next.js application
├── src/
│   ├── app/               # Pages (chat, admin, analytics, login)
│   ├── components/        # React components
│   ├── lib/               # API client, utils
│   ├── store/             # Zustand stores
│   └── types/             # TypeScript definitions
└── package.json
```

---

## 🚀 Core Features

✅ **Authentication** - Secure JWT-based login
✅ **RBAC** - Fine-grained role-based access control
✅ **RAG Pipeline** - Retrieval-Augmented Generation with ChromaDB
✅ **Streaming Chat** - Real-time token streaming via SSE
✅ **Analytics** - Chat history and usage tracking
✅ **Admin Panel** - User management and system configuration
✅ **Multi-Department** - Isolated document access by role
✅ **Vector Search** - Semantic similarity search with embeddings

---

## 📡 API Overview

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/auth/login` | POST | User login |
| `/auth/me` | GET | Get current user |
| `/chat/query` | POST | Standard chat query |
| `/chat/stream` | POST | Streaming chat query |
| `/analytics/chat-history` | GET | Query history |
| `/admin/users` | POST | Create user |
| `/health` | GET | Health check |
| `/docs` | GET | Interactive API docs (Swagger) |

👉 Full API docs at http://localhost:8000/docs

---

## ⚙️ Environment Variables

### Backend (.env)
```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/db

# API Keys
GROQ_API_KEY=your_groq_api_key

# JWT
JWT_SECRET_KEY=your_secret_key
JWT_EXPIRE_HOURS=8

# LLM & Embeddings
LLM_MODEL=llama-3.3-70b-versatile
EMBEDDING_MODEL=all-MiniLM-L6-v2

# Vector Store
CHROMA_DB_PATH=./chroma_db
TOP_K_RESULTS=5
CHUNK_SIZE=800
CHUNK_OVERLAP=150
```

### Frontend (.env.local)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## 🛠️ Development Commands

```bash
# Backend
cd backend && source venv/bin/activate
python -m uvicorn app.main:app --reload --port 8000
python ingestion/ingest.py              # Re-ingest documents
python -c "from app.database.init_db import init_database; init_database()"

# Frontend
cd frontend
npm run dev                             # Development server
npm run build                           # Production build
npm run start                           # Production server
npm run lint                            # Linting
```

---

## 📖 Full Documentation

This README is a quick reference. For complete setup instructions including:
- **Detailed macOS setup**
- **Detailed Windows setup**
- **PostgreSQL configuration**
- **Database schema details**
- **Complete API reference**
- **Troubleshooting guide**
- **Security best practices**

👉 **[See README_COMPLETE.md](README_COMPLETE.md)**

---

## 🐛 Common Issues

| Issue | Solution |
|-------|----------|
| `Connection refused` | Start PostgreSQL: `brew services start postgresql@15` |
| `ModuleNotFoundError` | Activate venv & reinstall: `pip install -r requirements.txt` |
| `GROQ_API_KEY not found` | Add key to `.env` file and restart |
| `Port 8000 already in use` | Kill process: `lsof -i :8000 \| grep LISTEN \| awk '{print $2}' \| xargs kill -9` |
| API returns 401 | Login again, token might be expired |

[→ More troubleshooting](README_COMPLETE.md#-troubleshooting)

---

## 🔒 Security

⚠️ **Before Production:**
- [ ] Change all default passwords
- [ ] Generate secure `JWT_SECRET_KEY`
- [ ] Set `DEBUG=False`
- [ ] Use environment-specific configs
- [ ] Enable HTTPS (use reverse proxy)
- [ ] Restrict CORS origins
- [ ] Rate limit API endpoints

[Full security guide →](README_COMPLETE.md#-security-recommendations)

---

## 📞 Resources

- [Groq API Docs](https://console.groq.com/docs)
- [FastAPI Docs](https://fastapi.tiangolo.com)
- [Next.js Docs](https://nextjs.org/docs)
- [PostgreSQL Docs](https://www.postgresql.org/docs)

---

## 📝 License

Proprietary - FoodChow Technologies

---

**Need detailed setup instructions?** → [📖 Read README_COMPLETE.md](README_COMPLETE.md)