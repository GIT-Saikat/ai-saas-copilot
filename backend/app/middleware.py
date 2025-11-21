"""
Middleware for rate limiting, error handling, and request logging.
Phase 4: API Development - Error Handling & Performance Optimization
"""

import time
import logging
import traceback
from typing import Callable
from fastapi import Request, Response, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
    ]
)
logger = logging.getLogger(__name__)

# Initialize rate limiter (FREE - in-memory)
limiter = Limiter(key_func=get_remote_address)


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Middleware for comprehensive error handling and logging."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and handle errors."""
        start_time = time.time()
        request_id = f"{int(time.time() * 1000)}-{id(request)}"
        
        # Log request
        logger.info(
            f"Request started",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "client": request.client.host if request.client else None,
            }
        )
        
        try:
            response = await call_next(request)
            
            # Calculate response time
            process_time = time.time() - start_time
            
            # Log successful response
            logger.info(
                f"Request completed",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": response.status_code,
                    "response_time_ms": round(process_time * 1000, 2),
                }
            )
            
            # Add response time header
            response.headers["X-Process-Time"] = str(round(process_time * 1000, 2))
            response.headers["X-Request-ID"] = request_id
            
            return response
            
        except HTTPException as e:
            # Handle FastAPI HTTP exceptions
            process_time = time.time() - start_time
            logger.warning(
                f"HTTP exception",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": e.status_code,
                    "detail": str(e.detail),
                    "response_time_ms": round(process_time * 1000, 2),
                }
            )
            return JSONResponse(
                status_code=e.status_code,
                content={
                    "error": True,
                    "message": e.detail,
                    "status_code": e.status_code,
                    "request_id": request_id,
                },
                headers={"X-Request-ID": request_id}
            )
            
        except Exception as e:
            # Handle unexpected errors
            process_time = time.time() - start_time
            error_traceback = traceback.format_exc()
            
            logger.error(
                f"Unexpected error",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                    "traceback": error_traceback,
                    "response_time_ms": round(process_time * 1000, 2),
                },
                exc_info=True
            )
            
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "error": True,
                    "message": "Internal server error",
                    "status_code": 500,
                    "request_id": request_id,
                },
                headers={"X-Request-ID": request_id}
            )


class TimeoutMiddleware(BaseHTTPMiddleware):
    """Middleware to handle request timeouts."""
    
    def __init__(self, app, timeout_seconds: float = 30.0):
        super().__init__(app)
        self.timeout_seconds = timeout_seconds
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Add timeout handling to requests."""
        import asyncio
        
        try:
            response = await asyncio.wait_for(
                call_next(request),
                timeout=self.timeout_seconds
            )
            return response
        except asyncio.TimeoutError:
            logger.error(
                f"Request timeout",
                extra={
                    "method": request.method,
                    "path": request.url.path,
                    "timeout_seconds": self.timeout_seconds,
                }
            )
            return JSONResponse(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                content={
                    "error": True,
                    "message": f"Request timeout after {self.timeout_seconds} seconds",
                    "status_code": 504,
                }
            )

