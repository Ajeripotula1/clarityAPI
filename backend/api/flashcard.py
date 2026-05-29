from fastapi import APIRouter, Depends
from models.schema import FlashcardResponse
from services.flashcards import generateFlashcards
from api.auth import get_current_user
router = APIRouter(
    prefix='/flashcards',
    tags=['flashcards']
)
@router.get('/flashcards', response_model=FlashcardResponse)
async def flashcard(file_name:str, user = Depends(get_current_user)):
    response = await generateFlashcards(file_name, user)
    print(response["flashcards"], type(response["flashcards"]))
    return FlashcardResponse(ok=response['ok'],flashcards=response['flashcards'] )