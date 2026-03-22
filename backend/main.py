from fastapi import FastAPI
from api import rag, upload, summary, flashcard
# main FastAPI instance
app = FastAPI()

# include the router
app.include_router(rag.router)
app.include_router(upload.router)
app.include_router(summary.router)
app.include_router(flashcard.router)

