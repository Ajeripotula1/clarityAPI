from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from services.ingestion import ingest
from pathlib import Path
from api.auth import get_current_user
from sqlalchemy.orm import Session
from database import get_db
from db_models import Documents
import uuid
router=APIRouter(
    prefix='/upload',
    tags=['upload']
)
# add current user and update path to include user name
# add to database and continue local storage
@router.post('/')
async def upload(file: UploadFile=File(...), user = Depends(get_current_user), db : Session = Depends(get_db)):
    if file.content_type != "application/pdf":
        raise HTTPException(400, "Only PDF supported currently.")
    
    Path(f"knowledgeBase/{user}").mkdir(exist_ok=True, parents=True)
    
    file_path = f"knowledgeBase/{user}/{file.filename}"
    
    print(f"Uploading {file_path} for {user}")
    
    with open(file_path, 'wb') as f:
        f.write(await file.read())
    
    success = ingest(user, file.filename, file_path)
    
    if success['ok']:
        # save file to database 
        # create Document entry obj
        new_doc = Documents(
            id = str(uuid.uuid4()),
            user_id=user,
            file_name = file.filename,
            storage_url = file_path,
        )
        print("adding entry to database: ", new_doc)
        db.add(new_doc)
        db.commit()
        db.refresh(new_doc)
        return {"ok": True, "messages":"File uploaded successfully"}            
    raise HTTPException(status_code=500, detail=f"Ingestion failed: {success.get('error', 'Unknown error')}")