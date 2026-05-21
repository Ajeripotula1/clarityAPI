from services.summarize import summarize_file
from langchain_core.prompts import PromptTemplate
from langchain_core.messages import HumanMessage
from core.config import llm, redis
from datetime import datetime, timedelta
import re, json, os

ttl = os.getenv("MEMORY_TTL")

async def generateFlashcards(file_name)-> list[dict]:
    """Generate Flashcard (Q&A pairs) based on summary for a document"""
    # check if we have recently cached flashcards 
    cache_key = f"flashcards:{file_name}"
    cached = await redis.get(cache_key)
    if cached:
        print("*** FLASHCARDS EXISTS IN CACHE ***")
        return {
                "ok": True,
                "flashcards": json.loads(cached)
            }
    
    # query summarize_file to get cached or newly generated summary for the document 
    summary = await summarize_file(file_name)
    # prompt LLM to generate Q&A pairs for user 
    prompt = f"""
        Based on the following summary of a document, generate 15 flashcards in JSON format. Each flashcard should have a **concise question and answer** that helps the user study key ideas and definitions from the summary.
        
        Return a list of flashcards like this:
        [
            {{"question": "...", "answer": "..."}}
            ...
        ]
        
        Summary:
        \"\"\"{summary['summary']}\"\"\"
        """
    response = llm.invoke(prompt)
    # print(response.content)
    # Parse the JSON string into a list of dicts
    content = response.content.strip()
    # Strip code block if present (e.g., ```json ... ```)
    if content.startswith("```"):
        content = re.sub(r"^```(?:json)?\s*", "", content)
        content = re.sub(r"\s*```$", "", content)

    try:
        flashcards = json.loads(content)
    except Exception as e:
        raise ValueError(f"Invalid JSON from model: {e}\n\nRaw content: {response.content}")
    # cache and return flashcards
    await redis.set(cache_key,json.dumps(flashcards),ex=ttl)
    return {"ok": True, "flashcards": flashcards}
        
    
    
    