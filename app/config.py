from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Database
    database_url: str
    
    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = int(os.getenv("PORT", "8000"))  # Support Render's PORT env var
    api_key: str  # Shared secret with Hono.js backend
    
    # Model Configuration
    model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
    embedding_dimension: int = 384  # all-MiniLM-L6-v2 dimension
    
    # Search Configuration
    similarity_threshold: float = 0.5
    max_results: int = 50
    
    # Redis Cache (optional)
    redis_url: Optional[str] = None
    cache_ttl: int = 3600  # 1 hour
    
    # Backend URL for webhooks (optional)
    backend_url: str = "http://localhost:3000"
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()