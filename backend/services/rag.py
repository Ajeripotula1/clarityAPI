from core.config import llm, vector_store, redis
from typing import Dict, List
import os, json
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

### This file contains the core logic for the RAG (Retrieval-Augmented Generation) system, including:
# - querying the vector store for relevant documents based on user queries
# - managing chat history and user memory to provide context for the LLM
# - generating responses using the LLM with retrieved context and chat history

# SESSION_STORE: Dict[str,List] = {} # session store for RAG, can be used to maintain separate chat histories for different users/sessions
k_docs = int(os.getenv('RELEVANT_DOCS_K', 3))
max_chat_history_len = int(os.getenv('CHAT_HISTORY_LENGTH'))

# chat history to maintain the order of conversation and provide context to the LLM for generating relevant responses. 
chat_history: List = []
# Summarized memory to be injected into prompt for context and relevant information
chat_memory = {
        "facts":[],
        "goals":[],
        "context":[],
        "topics":[]
}
# Getters and setter to maintain global chat history and memory    
def get_chat_history():
    return chat_history

def update_chat_history(updated_history:List):
    global chat_history 
    chat_history = updated_history

def get_chat_memory():
    return chat_memory

def update_chat_memory(updated_memory:Dict):
    global chat_memory
    chat_memory = updated_memory   
    



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
def query_vector_store(query: str, k: int=k_docs)-> dict:
    """Query the vector store for relevant documents based on the input query."""
    if not query:
        return {"ok": False, "error": "Empty query"}
    try:
        # Direct Chroma vector store call to retrieve relevant documents based on similarity search
        relevant_docs = vector_store.similarity_search(query, k=k)
        if not relevant_docs:
            return {"ok": True, "count": 0, "documents": []}
        docs_out = [
            {
                "source": d.metadata.get("source"),
                "page": d.metadata.get("page"),
                "text": d.page_content,
            }
            for d in relevant_docs
        ]
        return {"ok": True, "count": len(docs_out), "documents": docs_out}
    except Exception as err:
        return {"ok": False, "error": f"{type(err).__name__}: {err}"}

def rag_response(query:str, history):
    """Generate a RAG response by retrieving relevant documents from the vector store 
        and using them as context for the LLM to generate an answer."""
    # retrieve relevant chunks from the vector db
    res = query_vector_store(query)
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
    If the context does not contain information to answer the question, respond with: "I don't have enough information from the provided documents to answer that."
    """
    # - Include source references: [1], [2], ...

    try:
        # build history with RAG prompt for answer with context and previous conversation 
        messages_with_context = history + [HumanMessage(content=prompt)]
        response = llm.invoke(messages_with_context)
        answer = response.content
        print("RES ",answer)
        for doc in res['documents']:
            print(doc['text'])
        return {"ok": True, "answer": answer, "source_docs": res["documents"]}

    except Exception as err:
        return {"ok": False, "error": f"{type(err).__name__}: {err}"}

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

def query_llm(query:str):
    """Main function to handle a RAG query by managing the chat history, 
       retrieving relevant context, and generating a response using the LLM.
    """
    # retrieve global chat history and context
    chat = get_chat_history()
    # construct system message with injected context
    system_msg = generate_system_message(get_chat_memory())
    # construct messages with system message, chat history and current query
    messages = [system_msg] + chat
    # query LLM and get response, update chat history with new messages
    response = rag_response(query, messages)
    if not response['ok']:
        return {"ok": False, "error": response["error"]}
    
    # add current query to chat history to maintain order and context for future responses (w/o bloated query)
    chat.append(HumanMessage(content=query))
    # add the LLM response to chat history
    answer = response['answer']
    # print("ANSWER", answer)
    chat.append(AIMessage(content=answer))
    update_chat_history(chat)
    # print('final len', len(chat))
    # manage chat history length by summarizing older messages and maintaining recent messages when we reach capacity
    # once we are at capacity, we summarize the first half, and maintain the second half as it is 
    if len(chat) >= max_chat_history_len:
        print("overflow!", len(chat_history))
        old_msgs = chat[:max_chat_history_len//2]
        # pass 1st half to summarize and update memory
        updated_memory = summarize_history(get_chat_memory(), old_msgs)
        update_chat_memory(updated_memory)
        # keep ONLY recent after summarizing
        update_chat_history(chat[max_chat_history_len//2:])
        print('final len', len(chat), updated_memory)
    # for ch in chat_history:
    #     print(ch.content)
    # print("--DONE--")

    return {"ok": True, "answer": answer}
