from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, ForeignKey, create_engine, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os
from config import settings

Base = declarative_base()

# Database engine (will be configured later with Neon Postgres)
# For now, using SQLite for development
if settings.database_url:
    DATABASE_URL = settings.database_url
else:
    DATABASE_URL = "sqlite:///./textbook.db"

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    full_name = Column(String)
    hashed_password = Column(String)
    expertise_level = Column(String, default="beginner")  # beginner, intermediate, expert
    background = Column(String, default="both")  # software, hardware, both
    preferred_language = Column(String, default="en")  # en, ur
    learning_goals = Column(JSON, default=dict)  # JSON object with goals
    subscription_status = Column(String, default="free")  # free, premium
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    verification_token = Column(String, nullable=True)
    reset_token = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    chat_sessions = relationship("ChatSession", back_populates="user")
    questionnaire_responses = relationship("QuestionnaireResponse", back_populates="user")

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, expertise={self.expertise_level})>"

class QuestionnaireResponse(Base):
    __tablename__ = "questionnaire_responses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    question_id = Column(String)  # e.g., "q1_expertise", "q2_background"
    response = Column(JSON)  # Can be string, number, array, etc.
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="questionnaire_responses")

class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    conversation_id = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="chat_sessions")
    messages = relationship("ChatMessage", back_populates="session")

class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id"))
    role = Column(String)  # user, assistant, system
    content = Column(Text)
    message_metadata = Column(JSON)  # Additional metadata like sources, tokens, etc.
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    session = relationship("ChatSession", back_populates="messages")

class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(String, index=True)
    chunk_text = Column(Text)
    chunk_index = Column(Integer)
    embedding = Column(JSON)  # JSON array of floats
    chunk_metadata = Column(JSON)  # Source, module, page, etc.
    created_at = Column(DateTime, default=datetime.utcnow)

# Create tables
def create_tables():
    Base.metadata.create_all(bind=engine)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()