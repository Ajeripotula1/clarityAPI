from core.config import llm, vector_store, redis
from typing import Dict, List
import os, json
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, BaseMessage

### This file contains the core logic for the RAG (Retrieval-Augmented Generation) system, including:
# - querying the vector store for relevant documents based on user queries
# - managing chat history and user memory to provide context for the LLM
# - generating responses using the LLM with retrieved context and chat history

# how long(seconds) we keep chat memory and messages before they turn stale
ttl = os.getenv("MEMORY_TTL")

# SESSION_STORE: Dict[str,List] = {} # session store for RAG, can be used to maintain separate chat histories for different users/sessions
k_docs = int(os.getenv('RELEVANT_DOCS_K', 3))
max_chat_history_len = int(os.getenv('CHAT_HISTORY_LENGTH'))

EMPTY_MEMORY = {
        "facts":[],
        "goals":[],
        "context":[],
        "topics":[]
}

async def get_chat_history(user_id:str):
    # build key for chat history 
    chat_key = f"chat:{user_id}:history"
    # look up redis cache
    raw_chat = await redis.get(chat_key)
    # print(f"Looking chat up for {user_id}: {raw_chat}")
    # convert chat back into LangChain Messages for LLM
    return _deserialize_history(raw_chat) if raw_chat else []

async def set_chat_history(user_id, raw_chat):
    # convert LangChain messages into JSON string for storage and store
    # build key for chat history 
    chat_key = f"chat:{user_id}:history"
    await redis.set(chat_key, _serialize_history(raw_chat),ex=ttl)


async def get_chat_memory(user_id:str):
    """retrieve chat memory and convert it back to Py Obj"""
    # build key for chat memory 
    chat_key = f"chat:{user_id}:memory"
    # look up redis cache
    raw_memory = await redis.get(chat_key)
    # print(f"Looking memory up for {user_id}: {raw_memory}")
    # JSON str -> Py Obj
    return json.loads(raw_memory) if raw_memory else dict(EMPTY_MEMORY)

async def set_chat_memory(user_id, memory):
    """convert Py obj into JSON str for storage"""
    # build key for chat history 
    chat_key = f"chat:{user_id}:memory"
    await redis.set(chat_key, json.dumps(memory), ex=ttl)

def _serialize_history(messages: List[BaseMessage]) -> str:
    """Convert Obj into JSON String for data storage"""
    out = []
    # LangChain Messages obj -> dict
    for m in messages:
        if isinstance(m, HumanMessage):
            out.append({"role": "human", "content": m.content})
        elif isinstance(m, AIMessage):
            out.append({"role": "ai", "content": m.content})
    # Dict -> JSON str
    return json.dumps(out)

def _deserialize_history(raw: str) -> List[BaseMessage]:
    """Convert JSON String into obj to reconstruct LangChain msgs for sending to LLM"""
    if not raw:
        return []
    # JSON str -> DICT
    messages = json.loads(raw)
    llm_messages: List[BaseMessage] = []
    # DICT -> LangChain Messages
    for m in messages:
        if m["role"] == "human":
            llm_messages.append(HumanMessage(content=m["content"]))
        elif m["role"] == "ai":
            llm_messages.append(AIMessage(content=m["content"]))
    
    return llm_messages


def generate_system_message(memory:Dict):
    """Generate system message by injecting chat context into the base system prompt"""
    base_system_msg = "You are a helpful assistant, who answers questions based on context and refers to chat history or memory when necessary."
    system_msg = SystemMessage(
    content=f"""
    {base_system_msg}
    User Memory:
    Facts: {memory['facts']}
    Goals: {memory['goals']}
    Topics: {memory['topics']}
    Context: {memory['context']}
    """
    )
    return system_msg

# 4. query the vector store
def query_vector_store(query: str, user:str, k: int=k_docs)-> dict:
    """Query the vector store for relevant documents based on the input query."""
    if not query:
        return {"ok": False, "error": "Empty query"}
    try:
        # print("SEARCHING FOR: ", user)
        # build filter for user to ONLY query their documents 
        filter = {"user":user}
        # Direct Chroma vector store call to retrieve relevant documents based on similarity search
        relevant_docs = vector_store.similarity_search(
            query, 
            k=k,
            filter=filter
        )
        if not relevant_docs:
            return {"ok": True, "count": 0, "documents": []}
        docs_out = [
            {
                "source": d.metadata.get("source"),
                "page": d.metadata.get("page"),
                "user": d.metadata.get("user"),
                "text": d.page_content,
            }
            for d in relevant_docs
        ]
        return {"ok": True, "count": len(docs_out), "documents": docs_out}
    except Exception as err:
        return {"ok": False, "error": f"{type(err).__name__}: {err}"}

def rag_response(query:str, history, user):
    """Generate a RAG response by retrieving relevant documents from the vector store 
        and using them as context for the LLM to generate an answer."""
    # retrieve relevant chunks from the vector db
    res = query_vector_store(query, user)
    if not res['ok']:
        return {"ok":False, "error":res["error"]}
    # extract text from chunks and combine them to pass as context
    context = "\n\n".join([chunk['text']for chunk in res['documents']])
    # RAG prompt construction with clear instructions to ensure the LLM uses the provided context effectively
    prompt = f"""
    You are a factual AI assistant.
    Use only the provided context passages or consult the previous messages and user's memory if needed.
    Question:
    {query}
    Context:
    {context}
    Instructions:
    - Keep answer short (<200 words)
    - Use bullet points for multiple facts
    - Do not hallucinate
    If the context is incomplete, still answer using the relevant parts. Only say you don't have enough information if nothing is relevant.    """
    # - Include source references: [1], [2], ...

    try:
        # print("HAGA", prompt)
        # build history with RAG prompt for answer with context and previous conversation 
        messages_with_context = history + [HumanMessage(content=prompt)]
        response = llm.invoke(messages_with_context)
        answer = response.content
        # print("RES ",answer)
        # for doc in res['documents']:
        #     # print(doc['text'])
        return {"ok": True, "answer": answer, "source_docs": res["documents"]}

    except Exception as err:
        # print("caught error")
        return {"ok": False, "answer": f"{type(err).__name__}: {err}"}

# update memory to include the messages that will be "forgotten"
def summarize_history(memory, old_messages):
    """Summarize the chat history to update the user's memory by 
       extracting key facts, goals, context and topics from the conversation.
       This helps in maintaining important information while managing the chat history length."""
    formatted_messages = "\n".join([f"{m.type}: {m.content}" for m in old_messages]) # avoid LangChain message formatting to reduce token count 
    # prompt = f"""
    # You are updating a user's memory.
    # Current memory:
    # {memory}
    # New conversation:
    # {formatted_messages}
    # Extract and update:
    # - facts (stable truths about user)
    # - goals (what the user wants to accomplis with this conversation)
    # - context (important context)
    # - topics (what they discuss)
    # Return JSON only. Do not include any prose or markdown fences.
    # Schema:
    # {{"facts": [...], "goals": [...], "context": [...], "topics": [...]}}
    # """
    
    prompt = f"""
    You are summarizing the conversation history.
    Current memory:
    {memory}
    Conversation to summarize:
    {formatted_messages}
    Extract and update:
    - goals (user's objectives from chat)
    - context (key chat points)
    - topics (chat subjects)
    - facts (only user-related or chat-derived or user preferences for chat)
    Return JSON only. Do not include any prose or markdown fences.
    Schema: {{"facts": [...], "goals": [...], "context": [...], "topics": [...]}}
    """
    
    response = llm.invoke([HumanMessage(content=prompt)])
    # print('summarizing', formatted_messages, response.content, len(formatted_messages))
    try:
        return json.loads(response.content)
    except:
        print("Failed to parse JSON, keeping old memory")
        return memory

async def query_llm(query:str, user):
    """Main function to handle a RAG query by managing the chat history, 
       retrieving relevant context, and generating a response using the LLM.
    """
    # retrieve global chat history and context for specific user
    chat = await get_chat_history(user)
    memory = await get_chat_memory(user)
    # print('RETRIEVED: ', chat, memory)
    # construct system message with injected context
    system_msg = generate_system_message(memory)
    # construct messages with system message, chat history and current query
    messages = [system_msg] + chat
    # query LLM and get response, update chat history with new messages
    response = rag_response(query, messages, user)
    if not response['ok']:
        return {"ok": False, "error": response["error"]}
    
    # add current query to chat history to maintain order and context for future responses (w/o bloated query)
    chat.append(HumanMessage(content=query))
    # add the LLM response to chat history
    answer = response['answer']
    # print("ANSWER", answer)
    chat.append(AIMessage(content=answer))
    # manage chat history length by summarizing older messages and maintaining recent messages when we reach capacity
    # once we are at capacity, we summarize the first half, and maintain the second half as it is 
    if len(chat) >= max_chat_history_len:
        # print("overflow!", len(chat_history))
        old_msgs = chat[:max_chat_history_len//2]
        # pass 1st half to summarize and update memory
        updated_memory = summarize_history(memory, old_msgs)
        await set_chat_memory(user, updated_memory)
        # keep ONLY recent after summarizing
        chat = chat[max_chat_history_len//2:]
    await set_chat_history(user, chat)
    # print('final len', len(chat))
    # for ch in chat_history:
    #     print(ch.content)
    # print("--DONE--")

    return {"ok": True, "answer": answer}
