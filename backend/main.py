import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from api import rag, upload, summary, flashcard, auth, file_management
from core.config import redis
from database import engine

load_dotenv()

app = FastAPI(title="Clarity API")

cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in cors_origins.split(",") if o.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(rag.router)
app.include_router(upload.router)
app.include_router(summary.router)
app.include_router(flashcard.router)
app.include_router(file_management.router)


def _require_env(name: str) -> None:
    if not os.getenv(name):
        raise RuntimeError(f"Missing required environment variable: {name}")


@app.on_event("startup")
def validate_config() -> None:
    _require_env("SECRET_KEY")
    _require_env("OPENAI_API_KEY")
    _require_env("DATABASE_URL")


@app.get("/health")
def health():
    """Liveness — process is up."""
    return {"status": "ok"}


@app.get("/ready")
async def ready():
    """Readiness — Postgres and Redis reachable."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception as exc:
        return {"ready": False, "database": str(exc)}

    try:
        if not await redis.ping():
            return {"ready": False, "redis": "ping failed"}
    except Exception as exc:
        return {"ready": False, "redis": str(exc)}

    return {"ready": True, "database": "ok", "redis": "ok"}
