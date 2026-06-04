# 🧠 Clarity

## 🚀 Overview

**Turn dense notes into summaries, flashcards, and accurate answers — all grounded in your own data.**

Clarity is an AI-powered study assistant that uses Retrieval-Augmented Generation (RAG) to let users upload documents, ask context-aware questions, and generate structured learning outputs.

---

## 🎯 Problem

Effective studying requires understanding dense material, breaking it down, and reinforcing knowledge through active recall.

- Existing tools are fragmented (notes, flashcards, AI assistants)
- General AI tools can hallucinate or give irrelevant answers
- Constant context switching reduces learning efficiency

---

## 💡 Solution

Clarity centralizes studying into a single system powered by RAG:

- Retrieves relevant document chunks using vector similarity search
- Injects relevent context into LLM prompts to generate grounded responses
- Generates structured outputs (summaries, flashcards) from your uploaded content
- Support multi-turn, context-aware Q&A using conversational memory
- Caches expensive operations using Redis to reduce latency and API cost
- Supports multi user with JWT based authentication and per-user document isolation

---

## ⚙️ Features

- **Upload Files** — Add `.txt` and `.pdf` files to your knowledge base
- **Searchable Memory** — Semantic vector search using OpenAI embeddings + ChromaDB vector database
- **Chat with Your Notes** — Multi-turn Q&A with conversational memory and context groudning
- **Smart Summaries** — Extract Big Ideas, Key Terms, and concise takeaways from large documents
- **Flashcard Generator** — Automatically generate Q&A pairs for active recall and spaced repetition
- **Metadata Filtering** — Scoped retrieval per user and per document for percise, relevant results
- **Caching Layer** — Redis caching for faster responses and lower OpenAI API cost
- **Multi-User Auth** — JWT authentication with PostgreSQL-backed user and document persistence
- **Frontend UI (in progress)** — Clean, modular React interface

---
## 🖼️ How to Use

1. Upload your notes to the knowledge base
2. Generate summaries to extract key ideas and concepts
3. Ask questions and receive context-grounded answers
4. Generate flashcards for active recall and spaced repetition

---


## 🤖 Clarity uses

- **LLMs (via OpenAI GPT-4o mini LangChain)** to interpret queries and generate responses
- **ChromaDB** for semantic vector search across uploaded notes
- **FastAPI** for backend API and orchestration
- **Redis** for caching summaries, flashcards, and session conversations
- **PostgreSQL** for persisting user and document information 

> Answers are grounded in your uploaded material, which serves as the source of truth.

---

## 🧱 Tech Stack

| Area             | Tools               |
| ---------------- | ------------------- |
| **Backend**      | Python, FastAPI     |
| **LLM APIs**     | OpenAI GPT-4        |
| **RAG**          | LangChain           |
| **Embeddings**   | OpenAI Embeddings   |
| **Vector Store** | ChromaDB            |
| **Database**     | PostgreSQL          |
| **Caching**      | Redis               |

---

## 🏗️ How it Works

### Query Flow
 
```
User submits question
       ↓
Query embedded via OpenAI Embeddings
       ↓
Top-K chunks retrieved from ChromaDB (with metadata filtering)
       ↓
Conversational memory prepended to prompt
       ↓
LLM (GPT-4o mini via LangChain) generates grounded response
       ↓
Response cached in Redis (TTL-based)
```
 
### Ingestion Flow
 
```
User uploads document
       ↓
Document parsed and split into chunks
       ↓
Chunks embedded via OpenAI Embeddings
       ↓
Embeddings + metadata stored in ChromaDB
       ↓
File reference persisted to PostgreSQL
```
 
### Auth Flow
 
```
User registers / logs in
       ↓
JWT token issued and stored client-side
       ↓
Token verified on each protected route
       ↓
Requests scoped to authenticated user's documents
```

---

## 🚀 Getting Started
 
**Prerequisites:** Docker and Docker Compose
 
```bash
# Clone the repository
git clone https://github.com/Ajeripotula1/ClarityAPI
cd ClarityAPI/backend
 
# Configure environment
cp .env.example .env
# Fill in the required values (see Environment Variables below)
 
# Build and start all services (API + PostgreSQL + Redis)
docker compose up -d --build
```
 
The API will be available at `http://localhost:8000`. Postgres is exposed on `5433` (to avoid conflicts with a local instance) and Redis on `6379`.
 
> The API container waits for Postgres to pass its healthcheck before starting, so migrations run automatically via `entrypoint.sh` — no manual migration step needed.
 
### Environment Variables
 
Create a `.env` file in `backend/` with the following:
 
```env
# OpenAI
OPENAI_API_KEY=your_key_here
 
# Postgres
POSTGRES_USER=clarity
POSTGRES_PASSWORD=yourpassword
POSTGRES_DB=clarity_db
 
# Redis
REDIS_PASSWORD=yourredispassword
 
# Auth
JWT_SECRET_KEY=your_jwt_secret
```
 
> `DATABASE_URL` and `REDIS_HOST` are set automatically by Docker Compose and do not need to be added manually.
 
### Useful Commands
 
```bash
# View logs
docker compose logs -f api
 
# Stop all services
docker compose down
 
# Stop and remove volumes (full reset)
docker compose down -v
 
# Rebuild after code changes
docker compose up -d --build api
```
 
---

## 🔑 Key Concepts / Highlights

- Retrieval-Augmented Generation (RAG) for grounded AI responses
- Semantic search using vector embeddings (ChromaDB)
- Redis caching to optimize performance and reduce API cost
- Map-reduce summarization pipeline for large documents

---

## ⚠️ Challenges & Learnings

- Tuning chunk size and top-K retrieval for relevant context
- Reducing hallucinations through strict prompt grounding
- Managing API cost and latency with Redis caching
- Structuring large document summaries using map-reduce pipelines

---

## 🔮 Future Improvements (Coming soon)

- React UI
- Deployment to cloud infrastructure (AWS)
