from fastapi import APIRouter, Depends
from api.auth import get_current_user
from sqlalchemy.orm import Session
from database import get_db
from db_models import Documents
from models.schema import DocumentsResponse

router = APIRouter(
    prefix = '/manage',
    tags = ['management']
)

@router.get('/all')
async def get_all_files(user = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get all files for the current user's knowledge base"""
    docs = db.query(Documents).filter(Documents.user_id == user).all()
    print("output", docs)
    documents = []
    for doc in docs:
        print(doc, doc.user_id)
        documents.append(
            {
                "id": doc.id,
                "file_name": doc.file_name
            }
        )
    return DocumentsResponse(
        documents = documents,
        count = len(documents)
    )
    
@router.get('/delete')
async def get_all_files(id: str, user = Depends(get_current_user), db: Session = Depends(get_db)):
    """Deletes selected docuement from user's knowledge base"""
    # implement later 
    # delete from knowledge base (directory)
    # delete all releated chunks
    # delete redis summaries related to this 
    # delete from postgres DB



