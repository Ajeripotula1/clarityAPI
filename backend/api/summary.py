from fastapi import APIRouter, Depends
from models.schema import SummaryResponse
from services.summarize import summarize_file
from rich.console import Console
from rich.markdown import Markdown
from api.auth import get_current_user
router = APIRouter(
    prefix = '/summary',
    tags = ['summary']
)
@router.get('/', response_model=SummaryResponse)
async def summary(file_name:str,  user = Depends(get_current_user)):
    """Generate a summary for a given file"""
    print("summary for", file_name)
    response = await summarize_file(file_name, user)
    # print("RES", response)
    # console = Console()
    # md = Markdown(response['summary'])
    # console.print(md)
    return SummaryResponse(ok=response['ok'],summary=response['summary'])