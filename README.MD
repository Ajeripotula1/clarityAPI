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
- Injects context into LLM prompts to generate grounded responses
- Generates structured outputs (summaries, flashcards) from retrieved content
- Caches expensive operations using Redis to reduce latency and cost

---

## 🖼️ How to Use

1. Upload your notes to the knowledge base
2. Generate summaries to extract key ideas and concepts
3. Ask questions and receive context-grounded answers
4. Generate flashcards for active recall and spaced repetition

---

## ⚙️ Features

- 📂 **Upload Files** — Add `.txt` and `.pdf` files to your knowledge base
- 🔍 **Searchable Memory** — Uses embeddings + vector search for retrieval
- 💬 **Chat with Your Notes** — Ask questions and get context-grounded answers
- 🧠 **Smart Summaries** — Extract Big Ideas, Key Terms, and concise takeaways
- 🎓 **Flashcard Generator** — Automatically generate Q&A pairs for studying
- ⚡ **Caching Layer** — Redis caching for faster responses and lower cost
- 🌐 **Frontend UI (Coming Soon)** — Clean, modular React interface

---

## 🤖 How It Works

Clarity uses:

- **LLMs (via LangChain)** to interpret queries and generate responses
- **ChromaDB** for semantic vector search across uploaded notes
- **FastAPI** for backend API and orchestration
- **Redis** for caching summaries and flashcards

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
| **Frontend**     | React (coming soon) |
| **Caching**      | Redis               |

---

## 🏗️ Architecture

### Query Flow:

1. User submits a question
2. Query is embedded using OpenAI embeddings
3. Top-K relevant chunks are retrieved from ChromaDB
4. Retrieved context is injected into the LLM prompt
5. LLM generates a grounded response
6. Response is optionally cached in Redis

### Ingestion Flow:

1. User uploads document
2. Document is parsed and split into chunks
3. Chunks are converted into embeddings
4. Stored in ChromaDB for retrieval

---

## 🔑 Key Concepts / Highlights

- Retrieval-Augmented Generation (RAG) for grounded AI responses
- Semantic search using vector embeddings (ChromaDB)
- Redis caching to optimize performance and reduce API cost
- Map-reduce summarization pipeline for large documents

---

## ⚠️ Challenges & Learnings

Tuning chunk size and top-K retrieval for relevant context
Reducing hallucinations through strict prompt grounding
Managing API cost and latency with Redis caching
Structuring large document summaries using map-reduce pipelines

---

## 🚀 Getting Started

```bash
# Clone the repository
git clone https://github.com/Ajeripotula1/ClarityAPI
cd clarity

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create a .env file and configure:
MODEL=gpt-4o-mini
TEMPERATURE=0.7
OPENAI_API_KEY=your_key_here
CHAT_HISTORY_LENGTH=6
RELEVANT_DOCS_K=3
MEMORY_TTL=3600

# Start backend
uvicorn app.main:app --reload

# In a separate terminal, start Redis
redis-server
```

## 📂 Project Structure

```
clarityAPI/
    backend/
        api/ # routers for services
            upload.py
            rag.py
            summary.py
            flashcard.py

        core/
            config.py # llm, embeddings, vector DB, redis client setup
            db/
                chroma_db/ # persisted vector store
        knowledgeBase/ # where the user's uploaded file are stored for processing
            file1.pdf
            file2.pdf
            file3.pdf
        models/
            schema.py # Pydantic Models data validation
        services/ # Backend logic for features
            ingestion.py   # file processing, chunking, and storing to vector db
            summarize.py   # map reduce summary
            rag.py         # context driven chat with LLM
            flashcards.py  # Question answer pairs derived from summary
        .env
        main.py
        requirements.txt
        README.md
```

## 🔮 Future Improvements (Coming soon)

- React UI
- Long Term persistent memory (relational DB)
- Multi user support with JWT authentication
- Deployment to cloud infrastructure (AWS)
