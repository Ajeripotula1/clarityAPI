# Clarity — MVP deploy (Docker Compose)

Run the full stack from **`backend/`** (where `Dockerfile` and `docker-compose.yml` live).

## Prerequisites

- Docker Desktop (or Docker Engine + Compose v2)
- OpenAI API key
- A strong `SECRET_KEY` and `REDIS_PASSWORD`

## One-time setup

```bash
cd backend
cp .env.example .env
# Edit .env: OPENAI_API_KEY, SECRET_KEY, POSTGRES_PASSWORD, REDIS_PASSWORD
```

Generate a secret:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

## Start the stack

```bash
cd backend
docker compose up -d --build
```

- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- Postgres (host tools): `localhost:5433`
- Redis (host tools): `localhost:6379`

Migrations run automatically on API startup (`entrypoint.sh` → `alembic upgrade head`).

## Verify

```bash
curl http://localhost:8000/health
curl http://localhost:8000/ready
```

Register and get a token:

```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"demo","password":"secure-pass-123"}'

curl -X POST http://localhost:8000/auth/token \
  -d "username=demo&password=secure-pass-123"
```

Use `access_token` as `Authorization: Bearer <token>` on `/upload`, `/rag/query`, etc.

## Host dev (API outside Docker)

```bash
docker compose up -d db redis
# In .env set:
#   DATABASE_URL=postgresql+psycopg://postgres:YOUR_PASS@localhost:5433/clarity_db
#   REDIS_HOST=localhost
alembic upgrade head
uvicorn main:app --reload --port 8000
```

## Volumes

| Volume | Purpose |
|--------|---------|
| `knowledge_base` | Uploaded PDFs |
| `chroma_data` | Vector index |
| `postgres_data` | User/document tables |
| `redis_data` | Cache + chat history |

## Stop

```bash
docker compose down
# docker compose down -v   # also deletes volumes
```

## Cloud (next step)

Same image (`clarity-api`) can run on Railway, Fly.io, or ECS with managed Postgres/Redis. Point env vars at those hosts instead of `db` / `redis` service names.
