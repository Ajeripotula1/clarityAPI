from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker,declarative_base
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
# URL format: postgresql+psycopg://username:password@host:port/database
if not DATABASE_URL:
    raise ValueError("Database URL not found in environment variable")

# Create SQL Alchemy Engine
engine = create_engine(DATABASE_URL)

# Create Session Local client for database operations 
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for declarative models 
Base = declarative_base()

# Creates database session and yields to caller
# after execution completed, session is closed 
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


