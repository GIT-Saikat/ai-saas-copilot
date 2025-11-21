"""
Pydantic schemas for API request/response validation.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, EmailStr
from datetime import datetime


class ChunkMetadata(BaseModel):
    """Metadata for a retrieved document chunk."""
    id: str
    category: str
    source: Optional[str] = None


class Chunk(BaseModel):
    """A retrieved document chunk with score."""
    content: str
    score: float = Field(..., ge=0.0, le=1.0, description="Similarity score")
    metadata: ChunkMetadata


class QueryRequest(BaseModel):
    """Request schema for query endpoint."""
    query: str = Field(..., min_length=1, max_length=500, description="User question")
    user_session_id: Optional[str] = Field(None, description="Optional session identifier")


class QueryResponse(BaseModel):
    """Response schema for query endpoint."""
    query: str
    answer: str
    chunks: List[Chunk]
    blocked: bool = Field(default=False, description="Whether the query was blocked")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    response_time_ms: float = Field(..., ge=0, description="Response time in milliseconds")
    query_id: Optional[int] = Field(None, description="Database ID of logged query")


class FeedbackRequest(BaseModel):
    """Request schema for feedback endpoint."""
    query_id: int = Field(..., description="ID of the query to provide feedback for")
    feedback: str = Field(..., pattern="^(positive|negative)$", description="Feedback type")


class FeedbackResponse(BaseModel):
    """Response schema for feedback endpoint."""
    message: str
    query_id: int


class AnalyticsResponse(BaseModel):
    """Response schema for analytics endpoint."""
    total_queries: int
    avg_confidence: float
    blocked_queries: int
    positive_feedback: int
    negative_feedback: int
    avg_response_time_ms: float
    recent_queries: List[Dict[str, Any]]


class HealthResponse(BaseModel):
    """Response schema for health check endpoint."""
    status: str
    version: str
    timestamp: datetime = Field(default_factory=datetime.now)


# Authentication Schemas
class UserSignup(BaseModel):
    """Request schema for user signup."""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6, max_length=100)


class UserLogin(BaseModel):
    """Request schema for user login."""
    username: str
    password: str


class Token(BaseModel):
    """Response schema for authentication token."""
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    """Response schema for user information."""
    id: int
    email: str
    username: str
    is_active: bool
    created_at: datetime

