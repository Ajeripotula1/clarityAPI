from fastapi import APIRouter
from models.schema import ChatRequest, ChatResponse
from services.rag import query_llm

router=APIRouter(
    prefix='/rag',
    tags=['rag']
)

    
@router.post('/', response_model=ChatResponse)
def rag(payload:ChatRequest):
    response = query_llm(payload.query)
    # print(response)
    return ChatResponse(ok=response["ok"], answer=response["answer"])