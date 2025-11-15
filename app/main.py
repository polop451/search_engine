from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time
from typing import Optional

from app.config import settings
from app.database import init_db, get_db_connection
from app.embeddings import embedding_service
from app.search import search_service
from app.models import (
    SearchRequest,
    SearchResponse,
    IngredientSearchRequest,
    IngredientSearchResponse,
    EmbeddingRequest,
    EmbeddingResponse,
    HealthResponse
)

# Initialize FastAPI app
app = FastAPI(
    title="FitRecipes Vector Search API",
    description="Semantic search API for recipe recommendations using Sentence Transformers",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.backend_url, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Key verification
def verify_api_key(x_api_key: Optional[str] = Header(None)):
    """Verify API key from Hono.js backend"""
    if x_api_key != settings.api_key:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return x_api_key

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    """Initialize database and load model on startup"""
    print("🚀 Starting Vector Search API...")
    try:
        init_db()
        print("✅ Startup complete")
    except Exception as e:
        print(f"❌ Startup failed: {e}")
        raise

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    try:
        # Test database connection
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
                db_connected = True
    except:
        db_connected = False
    
    return HealthResponse(
        status="healthy" if db_connected else "degraded",
        model_loaded=embedding_service.model is not None,
        database_connected=db_connected
    )

@app.post("/search/vector", response_model=SearchResponse)
async def vector_search(
    request: SearchRequest,
    api_key: str = Depends(verify_api_key)
):
    """
    Semantic search endpoint using vector similarity
    
    - **query**: Search query text (e.g., "spicy thai chicken curry")
    - **limit**: Maximum number of results (1-50, default 10)
    - **filters**: Optional filters (mealType, difficulty, maxPrepTime, cuisineType)
    - **user_id**: Optional user ID for authorization
    """
    start_time = time.time()
    
    try:
        # Perform vector search
        results = search_service.search_recipes(
            query=request.query,
            limit=request.limit,
            filters=request.filters,
            user_id=request.user_id
        )
        
        execution_time = (time.time() - start_time) * 1000  # Convert to ms
        
        return SearchResponse(
            status="success",
            data=results,
            total=len(results),
            query=request.query,
            execution_time_ms=round(execution_time, 2)
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@app.post("/search/smart", response_model=SearchResponse)
async def smart_search(
    request: SearchRequest,
    api_key: str = Depends(verify_api_key)
):
    """
    🧠 SMART SEARCH: Natural Language Query Understanding + Vector Search
    
    **The most intelligent search endpoint** - automatically extracts filters from natural language:
    
    **Example Queries:**
    - "quick vegan thai dinner under 30 minutes"
      → Extracts: cuisineType=Thai, maxPrepTime=30, dietaryInfo.isVegan=true, mealType=DINNER
    
    - "easy gluten-free breakfast for beginners"
      → Extracts: difficulty=EASY, dietaryInfo.isGlutenFree=true, mealType=BREAKFAST
    
    - "spicy japanese curry with chicken"
      → Extracts: cuisineType=Japanese, cleaned query for semantic search
    
    - "keto lunch recipe ready in 20 minutes"
      → Extracts: dietaryInfo.isKeto=true, mealType=LUNCH, maxPrepTime=20
    
    **Features:**
    - 🎯 Auto-extracts time constraints, difficulty, cuisine, dietary requirements
    - 🔍 Expands query with synonyms for better semantic matching
    - 📊 Merges manual filters with auto-extracted filters (manual takes precedence)
    - ⚡ Multi-query ranking for enhanced relevance
    
    **Parameters:**
    - **query**: Natural language search query
    - **limit**: Maximum results (1-50, default 10)
    - **filters**: Optional manual filters (merged with auto-extracted)
    - **user_id**: Optional user ID for authorization
    
    **Response includes:**
    - `parsed_query`: Cleaned query after removing filter keywords
    - `extracted_filters`: Auto-detected filters from natural language
    """
    start_time = time.time()
    
    try:
        # Perform NLP-powered smart search
        results, parsed_query, extracted_filters = search_service.search_recipes_with_nlp(
            query=request.query,
            limit=request.limit,
            manual_filters=request.filters,
            user_id=request.user_id
        )
        
        execution_time = (time.time() - start_time) * 1000  # Convert to ms
        
        return SearchResponse(
            status="success",
            data=results,
            total=len(results),
            query=request.query,
            parsed_query=parsed_query,
            extracted_filters=extracted_filters,
            execution_time_ms=round(execution_time, 2)
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Smart search failed: {str(e)}")

@app.post("/search/ingredients", response_model=IngredientSearchResponse)
async def ingredient_search(
    request: IngredientSearchRequest,
    api_key: str = Depends(verify_api_key)
):
    """
    🥗 INGREDIENT-BASED SEARCH: Find recipes by ingredients
    
    Search for recipes that contain specific ingredients with intelligent matching.
    
    **Match Modes:**
    - `any` (OR): Recipes containing ANY of the specified ingredients
    - `all` (AND): Recipes containing ALL of the specified ingredients
    
    **Scoring System:**
    - Primary match (10 points): Exact mainIngredient match
    - Secondary match (5 points): mainIngredient contains ingredient
    - Tertiary match (3 points per): ingredients JSON array match
    - Quaternary match (2 points): Title contains ingredient
    - Quinary match (1 point): Description contains ingredient
    
    **Example Requests:**
    ```json
    // Find recipes with chicken OR garlic
    {
      "ingredients": ["chicken", "garlic"],
      "match_mode": "any",
      "limit": 10
    }
    
    // Find recipes with BOTH egg AND rice
    {
      "ingredients": ["egg", "rice"],
      "match_mode": "all",
      "limit": 5
    }
    
    // Find quick lunch with tomato
    {
      "ingredients": ["tomato"],
      "filters": {
        "mealType": ["LUNCH"],
        "maxPrepTime": 30
      }
    }
    ```
    
    **Parameters:**
    - **ingredients**: List of ingredient names (e.g., ["chicken", "garlic", "tomato"])
    - **match_mode**: "any" (default) or "all"
    - **limit**: Maximum results (1-50, default 10)
    - **filters**: Optional filters (mealType, difficulty, maxPrepTime, cuisineType)
    
    **Response includes:**
    - `match_score`: Ingredient match score (higher = better match)
    - `matched_count`: Number of ingredients matched
    """
    start_time = time.time()
    
    try:
        # Perform ingredient-based search
        results = search_service.search_by_ingredients(
            ingredients=request.ingredients,
            limit=request.limit,
            filters=request.filters,
            match_mode=request.match_mode
        )
        
        execution_time = (time.time() - start_time) * 1000  # Convert to ms
        
        return IngredientSearchResponse(
            status="success",
            data=results,
            total=len(results),
            ingredients=request.ingredients,
            match_mode=request.match_mode,
            execution_time_ms=round(execution_time, 2)
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingredient search failed: {str(e)}")

@app.post("/search/hybrid", response_model=SearchResponse)
async def hybrid_search(
    request: SearchRequest,
    api_key: str = Depends(verify_api_key)
):
    """
    Hybrid search combining keyword and vector similarity
    
    Best results for complex queries
    """
    start_time = time.time()
    
    try:
        results = search_service.hybrid_search(
            query=request.query,
            limit=request.limit,
            filters=request.filters
        )
        
        execution_time = (time.time() - start_time) * 1000
        
        return SearchResponse(
            status="success",
            data=results,
            total=len(results),
            query=request.query,
            execution_time_ms=round(execution_time, 2)
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@app.post("/embeddings/generate", response_model=EmbeddingResponse)
async def generate_embedding(
    request: EmbeddingRequest,
    api_key: str = Depends(verify_api_key)
):
    """
    Generate embedding for a specific recipe
    
    Called by Hono.js backend when new recipe is approved
    """
    try:
        # Fetch recipe from database (using 'recipes' table)
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT 
                        id, title, description, "mainIngredient",
                        ingredients, "cuisineType", "dietaryInfo", "mealType", allergies
                    FROM recipes 
                    WHERE id = %s AND status = 'APPROVED'
                """, (request.recipe_id,))
                
                recipe = cur.fetchone()
                
                if not recipe:
                    raise HTTPException(status_code=404, detail="Recipe not found or not approved")
        
        # Prepare text and generate embedding
        recipe_dict = dict(recipe)
        recipe_text = embedding_service.prepare_recipe_text(recipe_dict)
        embedding = embedding_service.generate_embedding(recipe_text)
        
        # Store embedding in database (using 'recipes' table)
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE recipes 
                    SET embedding = %s::vector 
                    WHERE id = %s
                """, (embedding, request.recipe_id))
                conn.commit()
        
        return EmbeddingResponse(
            status="success",
            recipe_id=request.recipe_id,
            embedding_generated=True,
            message=f"Embedding generated successfully for recipe {request.recipe_id}"
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Embedding generation failed: {str(e)}")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "FitRecipes Vector Search API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True
    )