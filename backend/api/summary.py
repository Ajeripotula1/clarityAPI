from fastapi import APIRouter
from models.schema import SummaryResponse
from services.summarize import summarize_file
from rich.console import Console
from rich.markdown import Markdown

router = APIRouter(
    prefix = '/summary',
    tags = ['summary']
)
@router.get('/', response_model=SummaryResponse)
async def summary(file_name:str):
    """Generate a summary for a given file"""
    response = await summarize_file(file_name)
    # print("RES", response)
    console = Console()
    md = Markdown(response['summary'])
    console.print(md)
    return SummaryResponse(ok=response['ok'],summary=response['summary'])