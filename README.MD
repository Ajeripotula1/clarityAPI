### System Design

# Key Features

1. Single File upload for knowledge base (store vectors)
2. RAG Q&A w/ chat bot
3. Conversation and context memory
4. Summarization
5. Q&A (flash card) pairs from data

# Endpoints

- POST /upload
- POST/chat
- GET /summary
- GET /flashcard

# Work Flow

- Users sends PDF file to endpoint and receives a confirmation
- Document split into chunks, vectorized and stored in vector DB
- User can sends question in the body of request
- Once question received, retrieve all relevant chunks and formulate prompt comprising of instruction, relevant context, and user's query to send to LLM
- send the response back to the user
- if users asks for summary, make sure we have data in the vector DB, then prompt LLM to summarize
- store summary locally (cache)
- if user asks for flashcards, query summary

# Structure

langchain/
clarityAPI/
app/
api/
v1/
endpoints/
upload.py
qa.py
summary.py
health.py
core/
config.py
logging.py
services/
ingestion.py
retrieval.py
rag.py
memory.py
models/
schema.py
db/
chroma_db/ # persisted vectors
**init**.py
main.py
tests/
test_upload.py
test_qa.py
test_memory.py
README.md
requirements.txt

# FlashCards

- Goal: user prompts a file they want to review, then get key value pairs for summarizing
- flow:
  - user send get request for a specific file
  - this should be cached as well
  - lets generate flashcards from summary
  - get summary if not cached
  - else generate it
  - prompt (for the given summary generate flashcards...)
