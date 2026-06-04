# Graph Report - /Users/akshayrajjeripotula/Desktop/AI_Engineering/langchain/clarity  (2026-05-21)

## Corpus Check
- Corpus is ~5,158 words - fits in a single context window. You may not need a graph.

## Summary
- 67 nodes · 80 edges · 15 communities (7 shown, 8 thin omitted)
- Extraction: 74% EXTRACTED · 26% INFERRED · 0% AMBIGUOUS · INFERRED: 21 edges (avg confidence: 0.83)
- Token cost: 8,000 input · 2,500 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Database & Auth|Database & Auth]]
- [[_COMMUNITY_Summarization & Cache|Summarization & Cache]]
- [[_COMMUNITY_API Schemas|API Schemas]]
- [[_COMMUNITY_Document Ingestion|Document Ingestion]]
- [[_COMMUNITY_RAG Chat Core|RAG Chat Core]]
- [[_COMMUNITY_Flashcards|Flashcards]]
- [[_COMMUNITY_Vector Retrieval|Vector Retrieval]]
- [[_COMMUNITY_App Entrypoint|App Entrypoint]]
- [[_COMMUNITY_Chat History|Chat History]]
- [[_COMMUNITY_System Prompts|System Prompts]]
- [[_COMMUNITY_RAG Concept|RAG Concept]]
- [[_COMMUNITY_Memory Summarization|Memory Summarization]]
- [[_COMMUNITY_Alembic Migrations|Alembic Migrations]]
- [[_COMMUNITY_Docker Compose|Docker Compose]]
- [[_COMMUNITY_LangChain Stack|LangChain Stack]]

## God Nodes (most connected - your core abstractions)
1. `query_llm()` - 12 edges
2. `ingest()` - 7 edges
3. `summarize_file()` - 6 edges
4. `generateFlashcards()` - 5 edges
5. `User` - 4 edges
6. `summary()` - 4 edges
7. `query_vector_store()` - 4 edges
8. `rag_response()` - 4 edges
9. `Documents` - 3 edges
10. `ChatResponse` - 3 edges

## Surprising Connections (you probably didn't know these)
- `ingest()` --conceptually_related_to--> `ChromaDB`  [INFERRED]
  services/ingestion.py → README.MD
- `Active Recall` --conceptually_related_to--> `generateFlashcards()`  [INFERRED]
  README.MD → services/flashcards.py
- `Map-Reduce Summarization` --conceptually_related_to--> `summarize_file()`  [INFERRED]
  README.MD → services/summarize.py
- `summarize_file()` --conceptually_related_to--> `Redis Caching`  [INFERRED]
  services/summarize.py → README.MD
- `ChromaDB` --conceptually_related_to--> `query_vector_store()`  [INFERRED]
  README.MD → services/rag.py

## Hyperedges (group relationships)
- **Clarity RAG Study Pipeline** — api_upload_upload, services_ingestion_ingest, services_rag_query_llm, services_summarize_summarize_file, services_flashcards_generateflashcards [INFERRED 0.85]
- **Production Migration Roadmap** — docs_production_migration_postgresql_persistence, docs_production_migration_jwt_authentication, docs_production_migration_multi_tenant_rag, docs_production_migration_docker_compose [EXTRACTED 1.00]

## Communities (15 total, 8 thin omitted)

### Community 0 - "Database & Auth"
Cohesion: 0.20
Nodes (8): upload(), get_db(), Documents, User, Base, JWT Authentication, PostgreSQL Persistence, User-Scoped Documents

### Community 1 - "Summarization & Cache"
Cohesion: 0.20
Nodes (7): Generate a summary for a given file, summary(), ChromaDB, Map-Reduce Summarization, Redis Caching, Generate Summary from all chunks that match input source, summarize_file()

### Community 2 - "API Schemas"
Cohesion: 0.27
Nodes (7): flashcard(), rag(), BaseModel, ChatRequest, ChatResponse, FlashcardResponse, SummaryResponse

### Community 3 - "Document Ingestion"
Cohesion: 0.48
Nodes (6): add_to_vectorDB(), chunk(), generate_id(), ingest(), process_file(), Reads text from a file, converts it into chunks, and stores them in vector DB

### Community 4 - "RAG Chat Core"
Cohesion: 0.43
Nodes (6): Multi-Tenant RAG, get_chat_memory(), query_llm(), Main function to handle a RAG query by managing the chat history,         retrie, update_chat_history(), update_chat_memory()

### Community 5 - "Flashcards"
Cohesion: 0.50
Nodes (3): Active Recall, generateFlashcards(), Generate Flashcard (Q&A pairs) based on summary for a document

### Community 6 - "Vector Retrieval"
Cohesion: 0.50
Nodes (4): query_vector_store(), rag_response(), Query the vector store for relevant documents based on the input query., Generate a RAG response by retrieving relevant documents from the vector store

## Knowledge Gaps
- **10 isolated node(s):** `Retrieval-Augmented Generation (RAG)`, `Map-Reduce Summarization`, `Active Recall`, `JWT Authentication`, `Alembic Migrations` (+5 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **8 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `ChromaDB` connect `Summarization & Cache` to `Document Ingestion`, `Vector Retrieval`?**
  _High betweenness centrality (0.424) - this node is a cross-community bridge._
- **Why does `ingest()` connect `Document Ingestion` to `Database & Auth`, `Summarization & Cache`?**
  _High betweenness centrality (0.375) - this node is a cross-community bridge._
- **Why does `query_vector_store()` connect `Vector Retrieval` to `Summarization & Cache`, `RAG Chat Core`?**
  _High betweenness centrality (0.279) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `query_llm()` (e.g. with `rag()` and `Multi-Tenant RAG`) actually correct?**
  _`query_llm()` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `ingest()` (e.g. with `upload()` and `ChromaDB`) actually correct?**
  _`ingest()` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `summarize_file()` (e.g. with `summary()` and `Map-Reduce Summarization`) actually correct?**
  _`summarize_file()` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `generateFlashcards()` (e.g. with `flashcard()` and `Active Recall`) actually correct?**
  _`generateFlashcards()` has 2 INFERRED edges - model-reasoned connections that need verification._