from fastapi import FastAPI
from api import rag, upload, summary, flashcard, auth
# from database import engine, Base
# import db_models
# main FastAPI instance
app = FastAPI()

# # look at all ORM models and create matching PostgreSQL tables
# Base.metadata.create_all(bind=engine)

# include the router
app.include_router(auth.router)
app.include_router(rag.router)
app.include_router(upload.router)
app.include_router(summary.router)
app.include_router(flashcard.router)

