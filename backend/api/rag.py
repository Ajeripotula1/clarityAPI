from fastapi import APIRouter, Depends
from models.schema import ChatRequest, ChatResponse
from services.rag import query_llm
from sqlalchemy import text
from api.auth import get_current_user
# Database connection dependency
from sqlalchemy.orm import Session
from database import get_db
from db_models import User

router=APIRouter(
    prefix='/rag',
    tags=['rag']
)

    
@router.post('/query', response_model=ChatResponse)
def rag(payload:ChatRequest, user = Depends(get_current_user)):
    print("testing,", user)
    response = query_llm(payload.query, user)
    # print(response)
    return ChatResponse(ok=response["ok"], answer=response["answer"])

@router.get("/health")
def db_health(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))  # from sqlalchemy import text
    return {"database": "ok"}