from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Database
    database_url: str = os.getenv("DATABASE_URL", "postgresql://localhost/searchdb")
    
    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = int(os.getenv("PORT", "8000"))  # Support Render's PORT env var
    api_key: str = os.getenv("API_KEY", "default-dev-key-change-in-production")
    
    # Model Configuration
    embedding_model_name: str = "sentence-transformers/all-MiniLM-L6-v2" 
    embedding_dimension: int = 384  # all-MiniLM-L6-v2 dimension
    
    # Search Configuration
    similarity_threshold: float = 0.4
    max_results: int = 50
    
    # Redis Cache (optional)
    redis_url: Optional[str] = None
    cache_ttl: int = 3600  # 1 hour
    
    # Backend URL for webhooks (optional)
    backend_url: str = "http://localhost:3000"
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        protected_namespaces = ('settings_',)  # Fix protected namespace warning

settings = Settings()
