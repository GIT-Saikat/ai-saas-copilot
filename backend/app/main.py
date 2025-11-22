"""
FastAPI application with RAG endpoints.
Phase 4: API Development - Complete implementation with error handling, rate limiting, and caching.
"""

from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Optional
from datetime import timedelta
import time
import logging

from app.config import settings, ACCESS_TOKEN_EXPIRE_MINUTES
from app.database import get_db, init_db, QueryLog, User
from app.schemas import (
    QueryRequest, QueryResponse, FeedbackRequest, FeedbackResponse,
    AnalyticsResponse, HealthResponse, Chunk,
    UserSignup, UserLogin, Token, UserResponse
)
from app.rag_pipeline import get_rag_pipeline
from app.auth import (
    get_password_hash, authenticate_user, create_access_token,
    get_current_active_user, get_current_user_required
)
from app.middleware import ErrorHandlingMiddleware, TimeoutMiddleware, limiter
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler
from app.cache import (
    get_cached_query, cache_query_result,
    get_cache_stats, clear_cache
)

# Configure logging
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="SaaS Support Copilot with RAG - Phase 4 Complete"
)

# Add rate limiter state
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Add middleware (order matters - error handling first, then timeout, then CORS)
app.add_middleware(ErrorHandlingMiddleware)
app.add_middleware(TimeoutMiddleware, timeout_seconds=30.0)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Initialize database and RAG pipeline on startup."""
    init_db()
    # Initialize RAG pipeline (this will load documents and build indices)
    get_rag_pipeline()
    print("Application started successfully")


@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint.
    
    Returns system health status and version information.
    """
    try:
        # Check database connection
        db = next(get_db())
        db.execute("SELECT 1")
        db.close()
        db_status = "healthy"
    except Exception as e:
        logger.warning(f"Database health check failed: {e}")
        db_status = "unhealthy"
    
    # Check RAG pipeline
    try:
        rag = get_rag_pipeline()
        rag_status = "healthy" if rag else "unhealthy"
    except Exception as e:
        logger.warning(f"RAG pipeline health check failed: {e}")
        rag_status = "unhealthy"
    
    overall_status = "healthy" if (db_status == "healthy" and rag_status == "healthy") else "degraded"
    
    return HealthResponse(
        status=overall_status,
        version=settings.app_version
    )


@app.get("/api/cache/stats")
async def get_cache_statistics():
    """
    Get cache statistics.
    
    Returns information about query and embedding cache usage.
    """
    return get_cache_stats()


@app.post("/api/cache/clear")
async def clear_all_caches():
    """
    Clear all caches.
    
    Admin endpoint to clear query and embedding caches.
    """
    cleared = clear_cache()
    return {
        "message": "Caches cleared successfully",
        "cleared": cleared
    }


# Authentication Endpoints
@app.post("/api/auth/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")  # Rate limit: 5 signups per minute per IP
async def signup(
    request: Request,
    user_data: UserSignup,
    db: Session = Depends(get_db)
):
    """
    Create a new user account.
    
    - **email**: User's email address
    - **username**: Unique username (3-50 characters)
    - **password**: Password (minimum 6 characters)
    """
    try:
        # Check if username already exists
        existing_user = db.query(User).filter(
            (User.username == user_data.username) | (User.email == user_data.email)
        ).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username or email already registered"
            )
        
        # Create new user
        hashed_password = get_password_hash(user_data.password)
        new_user = User(
            email=user_data.email,
            username=user_data.username,
            hashed_password=hashed_password,
            is_active=True
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        logger.info(f"New user created: {new_user.username} (ID: {new_user.id})")
        
        return UserResponse(
            id=new_user.id,
            email=new_user.email,
            username=new_user.username,
            is_active=new_user.is_active,
            created_at=new_user.created_at
        )
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        logger.error(f"Database error during signup: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database error. Please try again later."
        )
    except Exception as e:
        logger.error(f"Unexpected error during signup: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )


@app.post("/api/auth/login", response_model=Token)
@limiter.limit("10/minute")  # Rate limit: 10 login attempts per minute per IP
async def login(
    request: Request,
    credentials: UserLogin,
    db: Session = Depends(get_db)
):
    """
    Login and get access token.
    
    - **username**: Your username
    - **password**: Your password
    """
    try:
        user = authenticate_user(db, credentials.username, credentials.password)
        if not user:
            logger.warning(f"Failed login attempt for username: {credentials.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )
        
        logger.info(f"User logged in: {user.username} (ID: {user.id})")
        
        return {"access_token": access_token, "token_type": "bearer"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during login: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during login"
        )


@app.get("/api/auth/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user_required)):
    """Get current user information (requires authentication)."""
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        username=current_user.username,
        is_active=current_user.is_active,
        created_at=current_user.created_at
    )


@app.post("/api/query", response_model=QueryResponse, status_code=status.HTTP_200_OK)
@limiter.limit("60/minute")  # Rate limit: 60 queries per minute per IP
async def query(
    request: Request,
    query_request: QueryRequest,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_active_user)
):
    """
    Main query endpoint for question-answering with caching.
    
    - **query**: User's question
    - Returns answer with retrieved chunks and confidence score
    - Results are cached for 1 hour to improve performance
    """
    start_time = time.time()
    
    # Validate query
    if not query_request.query or not query_request.query.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Query cannot be empty"
        )
    
    if len(query_request.query) > 500:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Query is too long (max 500 characters)"
        )
    
    # Check cache first
    cached_result = get_cached_query(query_request.query)
    if cached_result:
        logger.info(f"Cache hit for query: {query_request.query[:50]}...")
        # Still log to database for analytics
        try:
            current_user_id = current_user.id if current_user else None
            query_log = QueryLog(
                query=query_request.query,
                answer=cached_result['answer'],
                top_similarity_score=cached_result['confidence'],
                num_chunks_retrieved=len(cached_result['chunks']),
                response_time_ms=(time.time() - start_time) * 1000,
                blocked=cached_result['blocked'],
                user_session_id=query_request.user_session_id,
                user_id=current_user_id
            )
            db.add(query_log)
            db.commit()
            db.refresh(query_log)
            cached_result['query_id'] = query_log.id
        except Exception as e:
            logger.warning(f"Error logging cached query: {e}")
        
        # Format chunks for response
        chunks = [
            Chunk(
                content=chunk['content'],
                score=chunk['score'],
                metadata=chunk['metadata']
            )
            for chunk in cached_result['chunks']
        ]
        
        return QueryResponse(
            query=query_request.query,
            answer=cached_result['answer'],
            chunks=chunks,
            blocked=cached_result['blocked'],
            confidence=cached_result['confidence'],
            response_time_ms=(time.time() - start_time) * 1000,
            query_id=cached_result.get('query_id')
        )
    
    # Cache miss - process query
    try:
        # Get RAG pipeline
        rag = get_rag_pipeline()
        
        # Process query
        result = rag.query(query_request.query)
        
        # Get current user if authenticated (optional)
        current_user_id = current_user.id if current_user else None
        
        # Log query to database
        try:
            query_log = QueryLog(
                query=query_request.query,
                answer=result['answer'],
                top_similarity_score=result['confidence'],
                num_chunks_retrieved=len(result['chunks']),
                response_time_ms=result['response_time_ms'],
                blocked=result['blocked'],
                user_session_id=query_request.user_session_id,
                user_id=current_user_id
            )
            db.add(query_log)
            db.commit()
            db.refresh(query_log)
        except SQLAlchemyError as e:
            logger.error(f"Database error logging query: {e}")
            db.rollback()
            query_log = None
        
        # Cache the result (without query_id as it's DB-specific)
        cache_data = {
            'answer': result['answer'],
            'chunks': result['chunks'],
            'blocked': result['blocked'],
            'confidence': result['confidence'],
            'response_time_ms': result['response_time_ms']
        }
        cache_query_result(query_request.query, cache_data)
        
        # Format chunks for response
        chunks = [
            Chunk(
                content=chunk['content'],
                score=chunk['score'],
                metadata=chunk['metadata']
            )
            for chunk in result['chunks']
        ]
        
        return QueryResponse(
            query=query_request.query,
            answer=result['answer'],
            chunks=chunks,
            blocked=result['blocked'],
            confidence=result['confidence'],
            response_time_ms=result['response_time_ms'],
            query_id=query_log.id if query_log else None
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing query: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Error processing query. Please try again later."
        )


@app.post("/api/feedback", response_model=FeedbackResponse, status_code=status.HTTP_200_OK)
@limiter.limit("30/minute")  # Rate limit: 30 feedback submissions per minute per IP
async def submit_feedback(
    request: Request,
    feedback_request: FeedbackRequest,
    db: Session = Depends(get_db)
):
    """
    Submit feedback for a query.
    
    - **query_id**: ID of the query to provide feedback for
    - **feedback**: Either "positive" or "negative"
    """
    try:
        # Validate query_id exists
        query_log = db.query(QueryLog).filter(QueryLog.id == feedback_request.query_id).first()
        if not query_log:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Query with id {feedback_request.query_id} not found"
            )
        
        # Update feedback
        query_log.feedback = feedback_request.feedback
        db.commit()
        
        logger.info(f"Feedback recorded: {feedback_request.feedback} for query_id {feedback_request.query_id}")
        
        return FeedbackResponse(
            message="Feedback recorded successfully",
            query_id=feedback_request.query_id
        )
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        logger.error(f"Database error recording feedback: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database error. Please try again later."
        )
    except Exception as e:
        logger.error(f"Error recording feedback: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while recording feedback"
        )


@app.get("/api/analytics", response_model=AnalyticsResponse)
@limiter.limit("30/minute")  # Rate limit: 30 analytics requests per minute per IP
async def get_analytics(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Get analytics data for the dashboard.
    
    Returns aggregated statistics about queries, confidence scores, feedback, etc.
    """
    try:
        # Get all query logs
        all_queries = db.query(QueryLog).all()
        
        if not all_queries:
            return AnalyticsResponse(
                total_queries=0,
                avg_confidence=0.0,
                blocked_queries=0,
                positive_feedback=0,
                negative_feedback=0,
                avg_response_time_ms=0.0,
                recent_queries=[]
            )
        
        # Calculate statistics
        total_queries = len(all_queries)
        
        # Average confidence (only for non-blocked queries)
        non_blocked = [q for q in all_queries if not q.blocked and q.top_similarity_score is not None]
        avg_confidence = (
            sum(q.top_similarity_score for q in non_blocked) / len(non_blocked)
            if non_blocked else 0.0
        )
        
        # Blocked queries
        blocked_queries = sum(1 for q in all_queries if q.blocked)
        
        # Feedback counts
        positive_feedback = sum(1 for q in all_queries if q.feedback == "positive")
        negative_feedback = sum(1 for q in all_queries if q.feedback == "negative")
        
        # Average response time
        avg_response_time = (
            sum(q.response_time_ms for q in all_queries) / total_queries
            if all_queries else 0.0
        )
        
        # Recent queries (last 20)
        recent_queries = [
            {
                "id": q.id,
                "query": q.query[:100] + "..." if len(q.query) > 100 else q.query,
                "confidence": q.top_similarity_score,
                "blocked": q.blocked,
                "feedback": q.feedback,
                "created_at": q.created_at.isoformat() if q.created_at else None
            }
            for q in sorted(all_queries, key=lambda x: x.created_at, reverse=True)[:20]
        ]
        
        return AnalyticsResponse(
            total_queries=total_queries,
            avg_confidence=round(avg_confidence, 3),
            blocked_queries=blocked_queries,
            positive_feedback=positive_feedback,
            negative_feedback=negative_feedback,
            avg_response_time_ms=round(avg_response_time, 2),
            recent_queries=recent_queries
        )
    
    except SQLAlchemyError as e:
        logger.error(f"Database error retrieving analytics: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database error. Please try again later."
        )
    except Exception as e:
        logger.error(f"Error retrieving analytics: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving analytics"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

