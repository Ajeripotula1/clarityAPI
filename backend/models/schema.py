from pydantic import BaseModel
from typing import List, Literal, Optional, Dict

class ChatRequest(BaseModel):
    query:str

class ChatResponse(BaseModel):
    ok: bool
    answer: Optional[str] = None

class SummaryResponse(BaseModel):
    ok: bool
    summary:Optional[str] = None
    
class FlashcardResponse(BaseModel):
    ok: bool
    flashcards: List[Dict]