"""
Configuration management for the application.
Loads environment variables and validates settings.
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field, field_validator


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Free Embedding Model (sentence-transformers)
    embedding_model: str = Field(
        default="all-MiniLM-L6-v2", 
        env="EMBEDDING_MODEL",
        description="Free sentence-transformers model for embeddings"
    )
    
    # Free LLM Model (Hugging Face)
    llm_model: str = Field(
        default="microsoft/DialoGPT-medium",
        env="LLM_MODEL",
        description="Free Hugging Face model for text generation"
    )
    
    # Hugging Face API (optional, for inference API - free tier)
    huggingface_api_key: Optional[str] = Field(
        default=None,
        env="HUGGINGFACE_API_KEY",
        description="Optional HF token for inference API (not required for local models)"
    )
    
    # Use Hugging Face Inference API (free tier) or local model
    use_hf_inference: bool = Field(
        default=False,
        env="USE_HF_INFERENCE",
        description="Use HF Inference API instead of local model"
    )
    
    # RAG Configuration
    similarity_threshold: float = Field(default=0.65, env="SIMILARITY_THRESHOLD")
    max_context_chunks: int = Field(default=5, env="MAX_CONTEXT_CHUNKS")
    variance_threshold: float = Field(default=0.1, env="VARIANCE_THRESHOLD")
    keyword_overlap_threshold: float = Field(default=0.2, env="KEYWORD_OVERLAP_THRESHOLD")
    
    # Database Configuration
    database_url: str = Field(
        default="sqlite:///./support_copilot.db",
        env="DATABASE_URL"
    )
    
    # Application Configuration
    app_name: str = "SaaS Support Copilot"
    app_version: str = "1.0.0"
    debug: bool = Field(default=False, env="DEBUG")
    
    # Hybrid Search Configuration
    vector_weight: float = Field(default=0.7, env="VECTOR_WEIGHT")
    bm25_weight: float = Field(default=0.3, env="BM25_WEIGHT")
    
    # LLM Generation Configuration
    temperature: float = Field(default=0.1, env="TEMPERATURE")
    max_tokens: int = Field(default=500, env="MAX_TOKENS")
    
    # Data Path
    data_path: str = Field(default="data/documentation.json", env="DATA_PATH")
    
    # Vector Store Persistence
    vector_index_path: str = Field(default="data/faiss_index.bin", env="VECTOR_INDEX_PATH")
    embeddings_path: str = Field(default="data/embeddings.npy", env="EMBEDDINGS_PATH")
    
    # JWT Authentication
    secret_key: str = Field(
        default="your-secret-key-change-in-production-use-random-string",
        env="SECRET_KEY"
    )
    algorithm: str = Field(default="HS256", env="ALGORITHM")
    access_token_expire_minutes: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    
    @field_validator("similarity_threshold")
    @classmethod
    def validate_threshold(cls, v):
        if not 0.0 <= v <= 1.0:
            raise ValueError("similarity_threshold must be between 0.0 and 1.0")
        return v
    
    @field_validator("max_context_chunks")
    @classmethod
    def validate_chunks(cls, v):
        if v < 1 or v > 20:
            raise ValueError("max_context_chunks must be between 1 and 20")
        return v
    
    @field_validator("vector_weight", "bm25_weight")
    @classmethod
    def validate_weights(cls, v):
        if not 0.0 <= v <= 1.0:
            raise ValueError("weights must be between 0.0 and 1.0")
        return v
    
    @field_validator("variance_threshold", "keyword_overlap_threshold")
    @classmethod
    def validate_thresholds(cls, v):
        if not 0.0 <= v <= 1.0:
            raise ValueError("thresholds must be between 0.0 and 1.0")
        return v
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"


# Global settings instance
settings = Settings()

# JWT constants for easy import
SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes

