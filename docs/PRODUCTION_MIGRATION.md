# Clarity — Production Migration Checklist

Branch strategy: implement on **`prod`** in small PRs; keep **`main`** stable for local dev until each chunk is verified.

**Last updated:** 2026-05-27

---

## Current state (snapshot)

| Area | Status |
|------|--------|
| **Branch** | `prod` — significant **uncommitted** work (auth, upload, scoping, Redis) |
| **Postgres** | Docker Compose — Postgres 16 on **5433**, volume persisted |
| **Redis** | Docker Compose — Redis 7 on **6379**, password via `REDIS_PASSWORD` |
| **Schema** | Alembic — `users`, `documents` (`file_name` column after rename migration) |
| **Auth** | `POST /auth/register`, `POST /auth/token`, JWT Bearer, `get_current_user` |
| **Protected routes** | upload, rag, summary, flashcards, file list — require token |
| **Documents** | Upload → `knowledgeBase/{user_id}/{filename}` + `documents` row |
| **Vector scope** | Chroma metadata `user` + filter on RAG/summary |
| **File listing** | `GET /manage/all` — user's documents from Postgres |
| **Deploy** | No `Dockerfile`, no API service in Compose, no CI/tests |

**Verdict:** Strong **local MVP feature set** (~**55–60%** toward deployable prod API). Auth + user-scoped storage/RAG work end-to-end on one machine. **Not deploy-ready** until bugs are fixed, chat is per-user, ops layer exists, and container story is complete.

---

## Progress tracker

| # | Chunk | Status | Depends on |
|---|--------|--------|------------|
| 0 | Baseline (main API) | **Done** | — |
| 1 | Boot & local Postgres + Redis | **~90%** | — |
| 2 | Alembic migrations | **~90%** | 1 |
| 3 | Auth (register / login / JWT) | **~85%** | 2 |
| 4 | Document metadata + local files | **~70%** | 3 |
| 5 | User-scoped vector retrieval | **~75%** | 4 |
| 6 | Session-scoped chat (Redis) | **~5%** | 3 |
| 7 | Env-based config | **~45%** | 1 |
| 8 | API hardening & ops | **~25%** | 3 |
| 9 | Tests & CI | Not started | 3, 4 |
| 10 | Deploy (Docker API + cloud) | Not started | 7, 8 |

---

## Mistakes & gaps to fix (before deploy)

These are concrete issues in the current codebase — fix before calling the API production-ready.

| Priority | Issue | Where | Fix |
|----------|--------|-------|-----|
| **High** | Global chat history shared across all users | `services/rag.py` | Per-user (or per-session) Redis keys — PR 6 |
| **High** | `SECRET_KEY` not validated at startup | `api/auth.py` | Fail fast if missing; use `JWT_SECRET` in `.env.example` |
| **High** | Summary/flashcards don't verify file in Postgres | `api/summary.py`, `api/flashcard.py` | Query `Documents` for `(user_id, file_name)` before Chroma |
| **High** | Flashcard route path wrong | `api/flashcard.py` | Prefix is `/flashcards` but route is `@router.get("/flashcards")` → **`/flashcards/flashcards`**. Change to `@router.get("/")` |
| **Medium** | Upload overwrites same filename | `api/upload.py` | Store as `knowledgeBase/{user_id}/{document_id}.pdf`; return `document_id` |
| **Medium** | DB row after ingest — orphan chunks if commit fails | `api/upload.py` | Insert document first (status=`processing`) or rollback file/chunks on failure |
| **Medium** | Delete endpoint stub + wrong HTTP method | `api/file_management.py` | `DELETE /manage/{id}`; implement file + Chroma + Redis + Postgres cleanup |
| **Medium** | Duplicate Python function name | `file_management.py` | Both routes named `get_all_files` — rename delete handler |
| **Medium** | Debug `print` in auth/RAG paths | `api/auth.py`, services | Remove or use logging |
| **Low** | `get_current_user` returns raw `user_id` string | `api/auth.py` | Optional: load `User` from DB; `/me` should return `UserResponse` |
| **Low** | `get_current_user` doesn't check user still exists | `api/auth.py` | DB lookup after JWT decode |
| **Low** | Auth logic lives in router, not `core/deps.py` | structure | Extract for reuse/tests (optional refactor) |
| **Low** | Alembic chain has 3 empty revisions + rename | `alembic/versions/` | Squash when convenient for fresh clones |
| **Low** | No `.env.example` | repo root / `backend/` | Document all required vars |
| **Low** | Redis/Chroma host hardcoded `localhost` | `core/config.py` | `REDIS_URL`, `CHROMA_PERSIST_DIR` from env — PR 7 |

---

## PR 1 — Boot & local Postgres + Redis

**Goal:** Infrastructure runs via Compose; app connects from host.

**Tasks**

- [x] `docker-compose.yml` — Postgres 16 (`5433:5432`)
- [x] `docker-compose.yml` — Redis 7 with password + volume
- [x] `requirements.txt` — `psycopg`, `alembic`, JWT/password libs
- [x] `database.py` — engine, `get_db()`
- [x] `core/config.py` — Redis client uses `REDIS_PASSWORD`
- [x] `.env` — `DATABASE_URL`, `POSTGRES_*`, `REDIS_PASSWORD`
- [ ] `.env.example` (no secrets)
- [ ] `README.MD` — Compose + uvicorn + alembic + auth flow
- [ ] `postgresql+psycopg://` in `DATABASE_URL` (optional consistency)

**Acceptance**

- [x] `docker compose up -d` → Postgres + Redis healthy
- [x] `GET /rag/health` → database ok
- [ ] Documented fresh-clone setup via `.env.example`

---

## PR 2 — Alembic migrations

**Goal:** Schema via migrations only.

**Tasks**

- [x] Alembic initialized; `env.py` imports `db_models`
- [x] Migration creates `users`, `documents`
- [x] Rename `filename` → `file_name` (`3c116f73c075`)
- [x] `create_all` removed from `main.py`
- [ ] Squash empty revisions (`862df…`, `798e…`, `14be…`) for cleaner history
- [ ] README: `alembic upgrade head`

**Acceptance**

- [x] `alembic upgrade head` → `users`, `documents` with `file_name`

---

## PR 3 — Authentication (JWT)

**Goal:** Protected API; users in Postgres.

**Implemented**

| Item | File |
|------|------|
| Register | `POST /auth/register` |
| Login | `POST /auth/token` (OAuth2 form) |
| Password hashing | `pwdlib` (Argon) |
| JWT | `PyJWT`, `sub` = user UUID |
| Dependency | `get_current_user` → Bearer token |
| Protected routers | upload, rag, summary, flashcard, manage |

**Tasks**

- [x] Register with hashed password + UUID `id`
- [x] Login returns bearer token
- [x] Feature routes require token
- [ ] Validate `SECRET_KEY` at startup
- [ ] `/auth/me` returns `UserResponse` (not raw id string)
- [ ] Move `get_current_user` to `core/deps.py` (optional)
- [ ] Remove debug prints

**Acceptance**

- [x] Unauthenticated upload → 401
- [x] Register → token → protected route works

---

## PR 4 — Document metadata + local `knowledgeBase/`

**Goal:** Postgres catalog + local PDFs (no S3 required).

**Implemented**

| Item | Status |
|------|--------|
| Path `knowledgeBase/{user_id}/{filename}` | Done |
| `Documents` row on successful upload | Done |
| `GET /manage/all` — list user's docs | Done |
| `storage_url` = relative path | Done |

**Tasks**

- [x] User-scoped directory
- [x] Insert `Documents` after ingest
- [x] List documents for current user
- [ ] Use `{document_id}.pdf` on disk (avoid overwrite)
- [ ] Return `document_id` from upload response
- [ ] Ownership check before summary/flashcard (Postgres)
- [ ] Implement delete (file + Chroma + Redis + row)
- [ ] Transaction / rollback on partial failure

**Acceptance**

- [x] Upload creates row + file under user's folder
- [ ] User cannot summarize a `file_name` they don't own (DB-enforced)

---

## PR 5 — User-scoped vector retrieval

**Goal:** RAG/summary only see caller's chunks.

**Implemented**

| Item | Status |
|------|--------|
| Ingest metadata `user`, `source`, `page` | Done |
| RAG `similarity_search(..., filter={"user": user})` | Done |
| Summary `where: user + source` | Done |
| Flashcard cache key includes `user` | Done |
| `query_llm(query, user)` | Done |

**Tasks**

- [x] Filter Chroma by `user` on query paths
- [ ] Add `document_id` to metadata (when PR 4 uses UUID paths)
- [ ] Re-ingest or reset Chroma if old chunks lack `user`

**Acceptance**

- [x] RAG retrieval scoped by user id in metadata
- [ ] Summary rejected for files not in user's `documents` table

---

## PR 6 — Session-scoped chat (Redis)

**Goal:** No shared global chat between users.

**Status:** **Not done** — `chat_history` / `chat_memory` still module globals in `services/rag.py`. **Blocker for multi-user deploy.**

**Tasks**

- [ ] Redis keys: `chat:{user_id}:{session_id}:history`
- [ ] Optional `session_id` on `ChatRequest`
- [ ] Remove global `chat_history`, `chat_memory`

**Acceptance**

- Two users with tokens do not see each other's conversation

---

## PR 7 — Environment-based configuration

**Tasks**

- [x] `DATABASE_URL`, `REDIS_PASSWORD` from env
- [ ] `REDIS_URL` (replace hardcoded `host="localhost"`)
- [ ] `CHROMA_PERSIST_DIR`, `KNOWLEDGE_BASE_DIR`
- [ ] `CORS_ORIGINS` on `main.py`
- [ ] `.env.example` with all vars

**Compose API service (later):** `DATABASE_URL=@db:5432`, `REDIS_URL=redis://:password@redis:6379`

---

## PR 8 — API hardening & observability

**Tasks**

- [x] `GET /rag/health` — DB ping
- [x] RAG moved to `POST /rag/query` (breaking vs old `POST /rag/`)
- [ ] `GET /health` (liveness) and `GET /ready` (DB + Redis) on `main.py`
- [ ] Async or thread pool for sync LLM in RAG
- [ ] Structured logging; remove route-level prints
- [ ] Global exception handler

---

## PR 9 — Tests & CI

**Status:** Not started.

**Minimum for MVP deploy confidence**

- [ ] `test_auth.py` — register, login, 401
- [ ] `test_upload.py` — upload creates document row
- [ ] `test_rag_scope.py` — user A cannot read user B chunks (mock Chroma)

---

## PR 10 — Deploy (Docker API)

**Status:** Not started.

**Tasks**

- [ ] `backend/Dockerfile`
- [ ] `api` service in `docker-compose.yml`
- [ ] Volumes: `knowledgeBase/`, `core/db/chroma_db/`
- [ ] `docs/DEPLOY.md` — single VM or Railway/Fly steps
- [ ] Run migrations on container start (entrypoint script)

**Acceptance**

- `docker compose up` → API + Postgres + Redis; upload + RAG work after register/login

---

## Deployable MVP API — definition of done

Minimum to ship a **single-server** MVP (one VM, Compose, or Railway):

### Must have (blockers)

1. [ ] Fix **flashcard route** path bug
2. [ ] **Per-user chat** in Redis (PR 6) — or disable chat history until done
3. [ ] **Postgres ownership check** on summary/flashcard
4. [ ] **`SECRET_KEY`** validated; `.env.example` committed
5. [ ] **`Dockerfile` + api service** in Compose with volume mounts
6. [ ] **`GET /ready`** — DB + Redis up
7. [ ] Remove **debug prints** from auth/RAG

### Should have (first week post-MVP)

8. [ ] Upload returns `document_id`; UUID-based file paths
9. [ ] Working **DELETE** document
10. [ ] **CORS** for frontend
11. [ ] **2–3 smoke tests** + basic CI
12. [ ] README with full setup flow

### Can wait (post-MVP)

- S3 storage
- Alembic squash
- Rate limiting
- Refresh tokens
- Hosted vector DB

---

## Suggested order (next 1–2 weeks)

```
1. Fix bugs (flashcard route, SECRET_KEY, ownership checks)
2. PR 6 — per-user Redis chat (critical for deploy)
3. PR 10 — Dockerfile + api in Compose + /ready
4. .env.example + README
5. PR 9 — minimal tests
6. Delete endpoint + document_id paths
```

---

## File map (current)

```
backend/
├── main.py                 # auth, rag, upload, summary, flashcard, file_management
├── database.py             # engine, get_db ✓
├── db_models.py            # User, Documents (file_name) ✓
├── docker-compose.yml      # postgres + redis ✓
├── alembic/                # migrations ✓
├── api/
│   ├── auth.py             # register, token, get_current_user ✓
│   ├── upload.py           # auth + Documents row ✓
│   ├── file_management.py  # list ✓; delete stub ✗
│   ├── rag.py              # POST /query, /health ✓
│   ├── summary.py          # auth ✓; no DB ownership check
│   └── flashcard.py        # route path bug ✗
├── core/
│   └── config.py           # llm, chroma, redis (localhost) 
└── services/
    ├── ingestion.py        # user in metadata ✓
    ├── rag.py              # user filter ✓; global chat ✗
    ├── summarize.py        # user filter ✓
    └── flashcards.py       # user in cache key ✓

knowledgeBase/{user_id}/     # local PDFs ✓
```

---

## Suggested merge order to `main`

1. Fix high-priority bugs + per-user chat  
2. Merge PRs **1–5** when ownership checks and flashcard route are fixed  
3. Merge **10 + 8 + 9** before any public URL  
4. Keep **main** as stable until Compose deploy is verified end-to-end

---

## Known gaps (do not deploy yet)

- [ ] Global chat history — all users share one conversation
- [ ] No Dockerfile / API container
- [ ] No tests or CI
- [ ] No `.env.example`
- [ ] Summary/flashcard not DB-gated for ownership
- [ ] Delete not implemented
- [ ] Flashcard URL likely wrong (`/flashcards/flashcards`)
- [ ] Re-upload same filename overwrites file and may duplicate/confuse Chroma ids
