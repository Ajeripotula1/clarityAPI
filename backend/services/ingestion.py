### This file contains the log for handling file uploads and processing for the RAG system, including:
# - processing the uploaded file to extract text and metadata
# - chunking the extracted text into smaller pieces for embedding and storage in the vector database
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
import pdfplumber, os, hashlib
from pathlib import Path
from core.config import vector_store
# --- 1. Process the file and extract text ---
def process_file(user:str, file_name:str, file_path)-> list[Document]:
    file_path = Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(f"knowledgeBase file not found: {file_path}")
    pages = []
    with pdfplumber.open(file_path) as pdf:
        # extract text from each page
        for i, page in enumerate(pdf.pages):
            text = page.extract_text() or ""
            # store page text content as Document obj w/ meta data 
            if text:
                # print("text: ",text)
                pages.append(
                    Document(
                        page_content=text.strip(),
                        # add use, page number, and file name for each chunk
                        metadata={"user": user, "page" : i+1,"source": file_name} 
                    )
                )
    # pass text content from all pages to be chunked 
    print(f"Extracted {len(pages)} pages")
    return pages
    
# --- 2. Chunk the text into equal logical chunks ---
def chunk(documents: list[Document])->list[Document]:
    # recursively split the document using common separators like new lines and punctuations
    # until each chunk is the appropriate size
    if not documents: return []
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100,
        add_start_index=True,
        separators=["\n\n","\n", "."," ", ""] # Define separators to split text in order of preference
    )
    
    chunks = text_splitter.split_documents(documents)
    print(f"Created {len(chunks)} chunks")
    return chunks 

# hash the chunks to ensure we don't add duplicates
def generate_id(doc):
    content = doc.page_content + str(doc.metadata)
    return hashlib.md5(content.encode()).hexdigest()

# --- 3.vectorize and store w/ deduplicate---
def add_to_vectorDB(chunks):
    if not chunks: return True
    # add all chunks to vector DB
    try:
        # generate unique binary hashes of chunk
        ids = [generate_id(doc) for doc in chunks]
        # pass chunks and their ids to DB, duplicates overwritten or ignored
        vector_store.add_documents(chunks, ids=ids)
        return True
    except Exception as err:
        print(f"add_documents failed: {type(err).__name__}: {err}")
        return False

def ingest(user, file_name, file_path):
    """Reads text from a file, converts it into chunks, and stores them in vector DB"""
    try:
        documents = process_file(user, file_name, file_path)
        if not documents:
            return {"ok": False, "error": "No pages extracted"}
        chunks = chunk(documents)
        if not chunks:
            return {"ok": False, "error": "Chunking produced no content"}
        success = add_to_vectorDB(chunks)
        return {"ok": success, "added_chunks": len(chunks) if success else 0}
    except FileNotFoundError as err:
        return {"ok": False, "error": str(err)}
    except Exception as err:
        return {"ok": False, "error": f"{type(err).__name__}: {err}"}

