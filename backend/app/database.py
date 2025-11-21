"""
Database models and session management using SQLAlchemy ORM.
Phase 4: API Development - Database Schema with relationship management.
"""

from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from typing import Optional, List

from app.config import settings

# Database setup
engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class User(Base):
    """
    Model for user accounts.
    Uses SQLAlchemy ORM for type safety and relationship management.
    """
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    
    # Relationship management: One user can have many query logs
    query_logs = relationship("QueryLog", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"


class QueryLog(Base):
    """
    Model for storing query logs and analytics.
    Uses SQLAlchemy ORM for type safety and relationship management.
    """
    
    __tablename__ = "query_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    query = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    top_similarity_score = Column(Float, nullable=True)
    num_chunks_retrieved = Column(Integer, default=0)
    response_time_ms = Column(Float, nullable=False)
    feedback = Column(String(20), nullable=True)  # 'positive', 'negative', or None
    blocked = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)
    user_session_id = Column(String(255), nullable=True)
    
    # Relationship management: Foreign key to User with relationship
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    user = relationship("User", back_populates="query_logs")
    
    def __repr__(self):
        return f"<QueryLog(id={self.id}, query='{self.query[:50]}...', blocked={self.blocked})>"


def init_db():
    """Initialize database by creating all tables."""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Dependency for getting database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

