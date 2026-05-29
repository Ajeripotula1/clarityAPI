from datetime import datetime, timedelta
# from langchain.chains.combine_documents import create_map_reduce_documents_chain
from core.config import vector_store as vector_db, llm as model
from langchain_core.documents import Document
from langchain_core.prompts import PromptTemplate
from core.config import redis
import os

# how long(seconds) we keep summaries before they turn stale
ttl = os.getenv("MEMORY_TTL")
async def summarize_file(file_name:str, user: str):
    """Generate Summary from all chunks that match input source"""
    print("running??")
    # Multi Page Summaries Process
    # Use Map Reduce:
        # Generate Summary of smaller chunks
        # Generate and return summary of summaries to be combined
    try:
        # check if summary exists in the cache 
        cache_key = f"summary:{file_name}"
        cached = await redis.get(cache_key)
        if cached:
            print("*** SUMMARY EXISTS IN CACHE ***")
            return {
                "ok": True,
                "summary": cached
            }
        
        # now = datetime.now()
        # cached = summary_cache.get(file_name)
        # # check if summary is cached and recent
        # if cached and now - cached["timestamp"] < SUMMARY_TTL:
        #     print("*** SUMMARY EXISTS IN CACHE ***")
        #     return {
        #         "ok": True,
        #         "summary": cached["summary"]
        #     }
        
        # Otherwise, generate and cache the summary
        print("*** GENERATING SUMMARY ***")    
        
        # query all relevant documents based on user AND the source name
        results = vector_db.get(where={
                "$and": [
                    {"user":user},
                    {"source": file_name}
                ]
            }
        )
            
        # convert retrieved dict into Document Obj
        source_documents = [
            Document(page_content=text, metadata=meta)
            for text, meta in zip(results["documents"], results["metadatas"])
        ]
        if not source_documents:
            return {"ok": False, "summary": ""}

       # Map step: summarize each chunk
        map_summaries = []
        map_prompt = PromptTemplate.from_template("""
            You're reviewing notes. Extract valuable content in the following structure:

            💡 Big Ideas:
            - Extract the most important insights.

            📘 Key Terms & Definitions:
            - List terms: **Term**: definition.

            🔄 Summary:
            - One-sentence summary.

            Note: {page_content}
        """)
        
        for doc in source_documents: 
            response = await model.ainvoke(map_prompt.format(page_content=doc.page_content))
            map_summaries.append(response.content)

        # Reduce step: combine summaries
        combined_text = "\n\n".join(map_summaries)
        reduce_prompt = PromptTemplate.from_template("""
            Summarize these chunk summaries into:

            ### 💡 **Big Ideas:**
            - Merged big ideas.

            ### 📘 **Key Terms & Definitions:**
            - Combined terms.

            ### 🔄 **Final Summary:**
            - 2–3 sentence high-level summary.

            Summaries: {combined}
        """)

        final_response = await model.ainvoke(reduce_prompt.format(combined=combined_text))
        summary = final_response.content

        # Cache summary to avoid re summarizing 
        await redis.set(cache_key,summary,ex=ttl)
        return {"ok": True, "summary": summary}
    

    except Exception as e:
        print(f"Error: {e}")
        return {"ok": False, "summary": ""}