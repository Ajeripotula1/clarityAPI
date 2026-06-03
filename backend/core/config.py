from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from dotenv import load_dotenv
import os
from langchain_chroma import Chroma
from redis.asyncio import Redis
load_dotenv()

model = os.getenv('MODEL')

redis_password = os.getenv("REDIS_PASSWORD")
redis_host = os.getenv("REDIS_HOST", "localhost")
redis_port = int(os.getenv("REDIS_PORT", "6379"))

temperature = os.getenv('TEMPERATURE')

llm = ChatOpenAI(model=model, temperature=temperature)

# Init the embedding model 
embedding_model = OpenAIEmbeddings(model='text-embedding-3-small')
# Get current directory and define directory for DB
current_dir = os.path.dirname(os.path.abspath(__file__)) # get current dir oc file for dynamic setup
persistent_directory = os.path.join(current_dir,"db","chroma_db") # directory where file will be created
# Ensure directory exists
os.makedirs(persistent_directory, exist_ok=True)    
# Create Vector store
vector_store = Chroma(
    collection_name='notes',
    embedding_function=embedding_model,
    persist_directory=persistent_directory
    )
print("Created Vector store ",vector_store._collection.count()) 

# Redis — use REDIS_HOST=redis inside Docker Compose
redis = Redis(
    host=redis_host,
    port=redis_port,
    password=redis_password,
    decode_responses=True,
)