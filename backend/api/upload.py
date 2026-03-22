from fastapi import APIRouter, UploadFile, File, HTTPException
from services.ingestion import ingest
from pathlib import Path
router=APIRouter(
    prefix='/upload',
    tags=['upload']
)
@router.post('/')
async def upload(file: UploadFile=File(...)):
    if file.content_type != "application/pdf":
        raise HTTPException(400, "Only PDF supported currently.")
    Path("knowledgeBase").mkdir(exist_ok=True, parents=True)
    file_path = f"knowledgeBase/{file.filename}"
    with open(file_path, 'wb') as f:
        f.write(await file.read())
    success = ingest(file.filename, file_path)
    if success['ok']:
        return {"ok": True, "messages":"File uploaded successfully"}            
    raise HTTPException(status_code=500, detail=f"Ingestion failed: {success.get('error', 'Unknown error')}")