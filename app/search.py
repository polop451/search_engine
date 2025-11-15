from typing import List, Optional, Dict, Any, Tuple
from app.database import get_db_connection, get_db_cursor
from app.embeddings import embedding_service
from app.config import settings
from app.nlp import parse_natural_language_query, expand_query_with_synonyms

class VectorSearchService:
    """Service for semantic search using vector similarity"""
    
    def search_recipes(
        self,
        query: str,
        limit: int = 10,
        filters: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Search recipes using semantic similarity
        
        Args:
            query: Search query text (e.g., "spicy thai chicken curry")
            limit: Maximum number of results
            filters: Optional filters (mealType, difficulty, cuisineType, maxPrepTime)
            user_id: Optional user ID for authorization
        
        Returns:
            List of recipes with similarity scores
        """
        # Generate query embedding
        query_embedding = embedding_service.generate_embedding(query)
        
        # Build SQL query - using 'recipes' table (Prisma @@map)
        # Column names use camelCase (Prisma default)
        sql = """
            SELECT 
                r.id,
                r.title,
                r.description,
                r."mainIngredient",
                r."cuisineType",
                r."mealType",
                r.difficulty,
                r."prepTime",
                r."cookingTime",
                r.servings,
                r."averageRating",
                r."totalRatings",
                r."imageUrls",
                r.status,
                r."authorId",
                1 - (r.embedding <=> %s::vector) as similarity
            FROM recipes r
            WHERE 
                r.status = 'APPROVED'
                AND r.embedding IS NOT NULL
        """
        params = [query_embedding]
        
        # Apply filters
        if filters:
            # Meal type filter (array overlap) - mealType is MealType[] array (enum type)
            if filters.get('mealType'):
                meal_types = filters['mealType']
                if isinstance(meal_types, list) and meal_types:
                    # Use && operator for array overlap with proper enum casting
                    placeholders = ','.join(['%s'] * len(meal_types))
                    sql += f" AND r.\"mealType\" && ARRAY[{placeholders}]::\"MealType\"[]"
                    params.extend(meal_types)
            
            # Difficulty filter (DifficultyLevel enum)
            if filters.get('difficulty'):
                difficulties = filters['difficulty']
                if isinstance(difficulties, list) and difficulties:
                    placeholders = ','.join(['%s'] * len(difficulties))
                    sql += f" AND r.difficulty = ANY(ARRAY[{placeholders}]::\"DifficultyLevel\"[])"
                    params.extend(difficulties)
            
            # Max prep time filter (prepTime + cookingTime)
            if filters.get('maxPrepTime'):
                sql += " AND (r.\"prepTime\" + r.\"cookingTime\") <= %s"
                params.append(filters['maxPrepTime'])
            
            # Cuisine type filter
            if filters.get('cuisineType'):
                sql += " AND LOWER(r.\"cuisineType\") = LOWER(%s)"
                params.append(filters['cuisineType'])
        
        # Add similarity threshold
        sql += f" AND (1 - (r.embedding <=> %s::vector)) >= %s"
        params.extend([query_embedding, settings.similarity_threshold])
        
        # Order by hybrid score: 70% similarity + 30% rating
        sql += """
            ORDER BY 
                (1 - (r.embedding <=> %s::vector)) * 0.7 + 
                (COALESCE(r."averageRating", 0) / 5.0) * 0.3 DESC
            LIMIT %s
        """
        params.extend([query_embedding, limit])
        
        # Execute query
        with get_db_connection() as conn:
            with get_db_cursor(conn) as cur:
                cur.execute(sql, params)
                results = cur.fetchall()
        
        return [dict(row) for row in results]
    
    def search_recipes_with_nlp(
        self,
        query: str,
        limit: int = 10,
        manual_filters: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None
    ) -> Tuple[List[Dict[str, Any]], str, Dict[str, Any]]:
        """
        🧠 SMART SEARCH: Natural Language Query Understanding + Vector Search
        
        Parses natural language queries to extract:
        - Time constraints: "under 30 minutes", "quick recipe"
        - Difficulty levels: "easy", "beginner friendly"
        - Dietary requirements: "vegan", "gluten-free", "keto"
        - Cuisine types: "Thai", "Italian", "Japanese"
        - Meal types: "breakfast", "dinner", "snack"
        
        Examples:
        - "quick vegan thai dinner under 30 minutes" → extracts cuisineType, maxPrepTime, dietaryInfo
        - "easy gluten-free breakfast for beginners" → extracts mealType, difficulty, dietaryInfo
        - "spicy japanese curry with chicken" → extracts cuisineType, cleans query
        
        Args:
            query: Natural language search query
            limit: Maximum number of results
            manual_filters: Optional manual filters (merged with auto-extracted)
            user_id: Optional user ID for authorization
        
        Returns:
            Tuple of (recipes, cleaned_query, extracted_filters)
        """
        # 1. Parse natural language query
        nlp_result = parse_natural_language_query(query)
        parsed_query = nlp_result['query']
        auto_filters = nlp_result['filters']
        dietary_info = nlp_result.get('dietaryInfo')
        
        # Add dietaryInfo to auto_filters if present
        if dietary_info:
            auto_filters['dietaryInfo'] = dietary_info
        
        # 2. Merge manual filters with auto-extracted filters (manual takes precedence)
        merged_filters = {**auto_filters, **(manual_filters or {})}
        
        # 3. Expand query with synonyms for better semantic matching
        expanded_queries = expand_query_with_synonyms(parsed_query)
        
        # 4. Search with each query variation and combine results
        all_results = {}
        
        for idx, search_query in enumerate(expanded_queries):
            # Generate embedding for this query variation
            results = self.search_recipes(
                query=search_query,
                limit=limit * 2,  # Get more results for merging
                filters=merged_filters,
                user_id=user_id
            )
            
            # Combine results with weighted scores
            weight = 1.0 / (idx + 1)  # Original query gets highest weight
            
            for recipe in results:
                recipe_id = recipe['id']
                similarity = recipe.get('similarity', 0)
                weighted_score = similarity * weight
                
                if recipe_id in all_results:
                    # Boost score if recipe appears in multiple query variations
                    all_results[recipe_id]['combined_score'] += weighted_score
                else:
                    recipe['combined_score'] = weighted_score
                    all_results[recipe_id] = recipe
        
        # 5. Sort by combined score and limit results
        ranked_results = sorted(
            all_results.values(),
            key=lambda x: x['combined_score'],
            reverse=True
        )[:limit]
        
        return ranked_results, parsed_query, auto_filters
    
    def search_by_ingredients(
        self,
        ingredients: List[str],
        limit: int = 10,
        filters: Optional[Dict[str, Any]] = None,
        match_mode: str = "any"
    ) -> List[Dict[str, Any]]:
        """
        🥗 INGREDIENT-BASED SEARCH: Find recipes by ingredients
        
        Searches recipes that contain specified ingredients with priority ranking:
        - Primary match: mainIngredient field
        - Secondary match: ingredients JSON array
        - Tertiary match: title and description
        
        Args:
            ingredients: List of ingredient names (e.g., ["chicken", "garlic", "tomato"])
            limit: Maximum number of results
            filters: Optional filters (mealType, difficulty, maxPrepTime, cuisineType)
            match_mode: "any" (OR - matches any ingredient) or "all" (AND - must match all)
        
        Returns:
            List of recipes sorted by ingredient match score
            
        Examples:
            - ingredients=["chicken", "garlic"] → recipes with chicken OR garlic
            - ingredients=["egg", "rice"], match_mode="all" → recipes with BOTH egg AND rice
        """
        if not ingredients:
            return []
        
        # Normalize ingredients to lowercase
        ingredients = [ing.strip().lower() for ing in ingredients if ing.strip()]
        
        if not ingredients:
            return []
        
        # Build SQL query with ingredient matching
        # Use subquery to allow ORDER BY to reference calculated columns
        sql = """
            SELECT * FROM (
                SELECT 
                    r.id,
                    r.title,
                    r.description,
                    r."mainIngredient",
                    r.ingredients,
                    r."cuisineType",
                    r."mealType",
                    r.difficulty,
                    r."prepTime",
                    r."cookingTime",
                    r.servings,
                    r."averageRating",
                    r."totalRatings",
                    r."imageUrls",
                    r.status,
                    r."authorId",
                    -- Calculate match score
                    (
                        -- Primary: mainIngredient exact match (weight: 10)
                        (CASE WHEN LOWER(r."mainIngredient") = ANY(%s) THEN 10 ELSE 0 END) +
                        
                        -- Secondary: mainIngredient contains any ingredient (weight: 5)
                        (CASE WHEN EXISTS (
                            SELECT 1 FROM unnest(%s) AS ing 
                            WHERE LOWER(r."mainIngredient") LIKE '%%' || ing || '%%'
                        ) THEN 5 ELSE 0 END) +
                        
                        -- Tertiary: ingredients JSON array match (weight: 3 per match)
                        (
                            SELECT COALESCE(COUNT(*), 0) * 3
                            FROM jsonb_array_elements(r.ingredients) AS ingredient
                            WHERE EXISTS (
                                SELECT 1 FROM unnest(%s) AS ing
                                WHERE LOWER(ingredient->>'name') LIKE '%%' || ing || '%%'
                            )
                        ) +
                        
                        -- Quaternary: title match (weight: 2)
                        (CASE WHEN EXISTS (
                            SELECT 1 FROM unnest(%s) AS ing
                            WHERE LOWER(r.title) LIKE '%%' || ing || '%%'
                        ) THEN 2 ELSE 0 END) +
                        
                        -- Quinary: description match (weight: 1)
                        (CASE WHEN EXISTS (
                            SELECT 1 FROM unnest(%s) AS ing
                            WHERE LOWER(r.description) LIKE '%%' || ing || '%%'
                        ) THEN 1 ELSE 0 END)
                    ) as match_score,
                    
                    -- Count how many ingredients matched
                    (
                        (CASE WHEN LOWER(r."mainIngredient") = ANY(%s) THEN 1 ELSE 0 END) +
                        (
                            SELECT COALESCE(COUNT(DISTINCT ing.val), 0)
                            FROM unnest(%s) AS ing(val)
                            WHERE EXISTS (
                                SELECT 1 FROM jsonb_array_elements(r.ingredients) AS ingredient
                                WHERE LOWER(ingredient->>'name') LIKE '%%' || ing.val || '%%'
                            )
                        )
                    ) as matched_count
                    
                FROM recipes r
                WHERE 
                    r.status = 'APPROVED'
            ) AS recipe_matches
            WHERE match_score > 0
        """
        
        # Pass ingredients array 7 times for different parts of the query
        params = [ingredients, ingredients, ingredients, ingredients, ingredients, ingredients, ingredients]
        
        # Add match_mode filter
        if match_mode == "all":
            # Must match ALL ingredients
            sql += " AND matched_count >= %s"
            params.append(len(ingredients))
        
        # Apply additional filters
        if filters:
            if filters.get('mealType'):
                meal_types = filters['mealType']
                if isinstance(meal_types, list) and meal_types:
                    placeholders = ','.join(['%s'] * len(meal_types))
                    sql += f" AND \"mealType\" && ARRAY[{placeholders}]::\"MealType\"[]"
                    params.extend(meal_types)
            
            if filters.get('difficulty'):
                difficulties = filters['difficulty']
                if isinstance(difficulties, list) and difficulties:
                    placeholders = ','.join(['%s'] * len(difficulties))
                    sql += f" AND difficulty = ANY(ARRAY[{placeholders}]::\"DifficultyLevel\"[])"
                    params.extend(difficulties)
            
            if filters.get('maxPrepTime'):
                sql += " AND (\"prepTime\" + \"cookingTime\") <= %s"
                params.append(filters['maxPrepTime'])
            
            if filters.get('cuisineType'):
                sql += " AND LOWER(\"cuisineType\") = LOWER(%s)"
                params.append(filters['cuisineType'])
        
        # Order by match score (70%) + rating (30%)
        sql += """
            ORDER BY 
                match_score * 0.7 + (COALESCE("averageRating", 0) / 5.0) * 0.3 DESC,
                matched_count DESC
            LIMIT %s
        """
        params.append(limit)
        
        # Execute query
        with get_db_connection() as conn:
            with get_db_cursor(conn) as cur:
                cur.execute(sql, params)
                results = cur.fetchall()
        
        return [dict(row) for row in results]

    def hybrid_search(
        self,
        query: str,
        limit: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Hybrid search combining keyword and vector search
        
        Best results for complex queries - uses PostgreSQL full-text search
        combined with vector similarity
        """
        # 1. Vector search (semantic understanding)
        vector_results = self.search_recipes(query, limit * 2, filters)
        
        # 2. Keyword search (exact matches)
        keyword_results = self._keyword_search(query, limit * 2, filters)
        
        # 3. Merge and re-rank results
        combined_scores = {}
        
        # Add vector scores (weight: 0.6)
        for recipe in vector_results:
            recipe_id = recipe['id']
            combined_scores[recipe_id] = {
                'recipe': recipe,
                'score': recipe.get('similarity', 0) * 0.6
            }
        
        # Add keyword scores (weight: 0.4)
        for recipe in keyword_results:
            recipe_id = recipe['id']
            rank = recipe.get('rank', 0)
            
            if recipe_id in combined_scores:
                combined_scores[recipe_id]['score'] += rank * 0.4
            else:
                combined_scores[recipe_id] = {
                    'recipe': recipe,
                    'score': rank * 0.4
                }
        
        # Sort by combined score
        ranked_results = sorted(
            combined_scores.values(),
            key=lambda x: x['score'],
            reverse=True
        )[:limit]
        
        return [item['recipe'] for item in ranked_results]
    
    def _keyword_search(
        self,
        query: str,
        limit: int,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Internal method for PostgreSQL full-text keyword search
        Uses 'recipes' table (Prisma @@map)
        """
        # Prepare query for PostgreSQL full-text search
        search_query = ' & '.join(query.split())
        
        sql = """
            SELECT 
                r.*,
                ts_rank(
                    to_tsvector('english', 
                        COALESCE(r.title, '') || ' ' || 
                        COALESCE(r.description, '') || ' ' || 
                        COALESCE(r."mainIngredient", '')
                    ),
                    to_tsquery('english', %s)
                ) as rank
            FROM recipes r
            WHERE 
                r.status = 'APPROVED'
                AND to_tsvector('english', 
                    COALESCE(r.title, '') || ' ' || 
                    COALESCE(r.description, '') || ' ' || 
                    COALESCE(r."mainIngredient", '')
                ) @@ to_tsquery('english', %s)
        """
        params = [search_query, search_query]
        
        # Apply same filters as vector search
        if filters:
            if filters.get('mealType'):
                meal_types = filters['mealType']
                if isinstance(meal_types, list) and meal_types:
                    placeholders = ','.join(['%s'] * len(meal_types))
                    sql += f" AND r.\"mealType\" && ARRAY[{placeholders}]::\"MealType\"[]"
                    params.extend(meal_types)
            
            if filters.get('difficulty'):
                difficulties = filters['difficulty']
                if isinstance(difficulties, list) and difficulties:
                    placeholders = ','.join(['%s'] * len(difficulties))
                    sql += f" AND r.difficulty = ANY(ARRAY[{placeholders}]::\"DifficultyLevel\"[])"
                    params.extend(difficulties)
            
            if filters.get('maxPrepTime'):
                sql += " AND (r.\"prepTime\" + r.\"cookingTime\") <= %s"
                params.append(filters['maxPrepTime'])
            
            if filters.get('cuisineType'):
                sql += " AND LOWER(r.\"cuisineType\") = LOWER(%s)"
                params.append(filters['cuisineType'])
        
        sql += " ORDER BY rank DESC LIMIT %s"
        params.append(limit)
        
        with get_db_connection() as conn:
            with get_db_cursor(conn) as cur:
                cur.execute(sql, params)
                results = cur.fetchall()
        
        return [dict(row) for row in results]

# Global instance
search_service = VectorSearchService()