from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class SearchRequest(BaseModel):
    """Request model for recipe search"""
    query: str = Field(..., min_length=1, max_length=500, description="Natural language search query")
    limit: int = Field(default=10, ge=1, le=50, description="Maximum results")
    filters: Optional[Dict[str, Any]] = Field(default=None, description="Optional filters")
    user_id: Optional[str] = Field(default=None, description="User ID for authorization")

class SearchResponse(BaseModel):
    """Response model for recipe search"""
    status: str = "success"
    data: List[Dict[str, Any]]
    total: int
    query: str
    parsed_query: Optional[str] = None  # Cleaned query after NLP parsing
    extracted_filters: Optional[Dict[str, Any]] = None  # Auto-extracted filters
    execution_time_ms: float

class IngredientSearchRequest(BaseModel):
    """Request model for ingredient-based search"""
    ingredients: List[str] = Field(..., min_length=1, description="List of ingredients to search for")
    limit: int = Field(default=10, ge=1, le=50, description="Maximum results")
    filters: Optional[Dict[str, Any]] = Field(default=None, description="Optional filters (mealType, difficulty, maxPrepTime, cuisineType)")
    match_mode: str = Field(default="any", pattern="^(any|all)$", description="Match mode: 'any' (OR) or 'all' (AND)")

class IngredientSearchResponse(BaseModel):
    """Response model for ingredient-based search"""
    status: str = "success"
    data: List[Dict[str, Any]]
    total: int
    ingredients: List[str]
    match_mode: str
    execution_time_ms: float

class EmbeddingRequest(BaseModel):
    """Request model for embedding generation"""
    recipe_id: str = Field(..., description="Recipe ID to generate embedding for")

class EmbeddingResponse(BaseModel):
    """Response model for embedding generation"""
    status: str = "success"
    recipe_id: str
    embedding_generated: bool
    message: str

class HealthResponse(BaseModel):
    """Health check response"""
    status: str = "healthy"
    model_loaded: bool
    database_connected: bool
    version: str = "1.0.0"