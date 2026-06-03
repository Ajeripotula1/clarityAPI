from sqlalchemy import Column, BigInteger, String, DateTime, ForeignKey
from datetime import datetime, UTC
from database import Base

# map python to PostgreSQL table
class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, nullable=False)
    username = Column(String, unique=True, nullable=False)
    # hashed password 
    password = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC))

class Documents(Base):
    __tablename__ = "documents"
    
    id = Column(String, primary_key=True, nullable=False)
    # link to user 
    user_id = Column(String, ForeignKey('users.id'), nullable=False)
    file_name = Column(String, nullable=False)
    storage_url = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC))