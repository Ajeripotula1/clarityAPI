from pydantic import BaseModel
from typing import List, Literal, Optional, Dict


class UserBase(BaseModel):
    username:str

class UserCreate(UserBase):
    password:str

# allow ORM objs to be returned as well 
class UserResponse(UserBase):
    id:str

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token:str
    token_type:str

class DocumentsResponse(BaseModel):
    documents: List[Dict]
    count:int

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