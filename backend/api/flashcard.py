from fastapi import APIRouter
from models.schema import FlashcardResponse
from services.flashcards import generateFlashcards
router = APIRouter(
    prefix='/flashcards',
    tags=['flashcards']
)
@router.get('/', response_model=FlashcardResponse)
async def flashcard(file_name:str):
    response = await generateFlashcards(file_name)
    print(response["flashcards"], type(response["flashcards"]))
    return FlashcardResponse(ok=response['ok'],flashcards=response['flashcards'] )