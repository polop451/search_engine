from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any
import numpy as np
import torch
from app.config import settings

class EmbeddingService:
    """Service for generating embeddings using Sentence Transformers"""
    
    def __init__(self):
        print(f"📦 Loading model: {settings.model_name}")
        
        # Detect best device (MPS > CUDA > CPU)
        if torch.backends.mps.is_available() and torch.backends.mps.is_built():
            device = 'mps'  # Apple Silicon GPU acceleration
            print("🚀 Using Apple Silicon GPU (MPS)")
        elif torch.cuda.is_available():
            device = 'cuda'  # NVIDIA GPU
            print("🚀 Using NVIDIA GPU (CUDA)")
        else:
            device = 'cpu'
            print("⚠️  Using CPU (no GPU acceleration)")
        
        self.model = SentenceTransformer(settings.model_name, device=device)
        self.device = device
        print(f"✅ Model loaded on {device}")
    
    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for a single text"""
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding.tolist()
    
    def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts (more efficient)"""
        embeddings = self.model.encode(
            texts, 
            convert_to_numpy=True, 
            show_progress_bar=True,
            batch_size=32  # Optimized for most hardware
        )
        return embeddings.tolist()
    
    def prepare_recipe_text(self, recipe: Dict[str, Any]) -> str:
        """
        Prepare recipe text for embedding generation
        Combines title, description, ingredients, cuisine, and dietary info
        Matches Prisma schema column names (camelCase)
        """
        # Extract ingredients from JSON array
        ingredients_data = recipe.get('ingredients', [])
        if isinstance(ingredients_data, list):
            ingredients = ", ".join([
                ing.get('name', '') if isinstance(ing, dict) else str(ing) 
                for ing in ingredients_data
            ])
        else:
            ingredients = str(ingredients_data)
        
        # Build comprehensive text representation - using Prisma field names
        text_parts = [
            recipe.get('title', ''),
            recipe.get('description', ''),
            f"Main ingredient: {recipe.get('mainIngredient', '')}",
            f"Ingredients: {ingredients}",
            f"Cuisine: {recipe.get('cuisineType', '')}",
        ]
        
        # Add meal type information - mealType is array in Prisma
        meal_type = recipe.get('mealType', [])
        if meal_type:
            if isinstance(meal_type, list):
                text_parts.append(f"Meal type: {', '.join(meal_type)}")
            else:
                text_parts.append(f"Meal type: {meal_type}")
        
        # Add dietary information from JSON - dietaryInfo in Prisma
        dietary_info = recipe.get('dietaryInfo', {})
        if isinstance(dietary_info, dict):
            dietary_labels = []
            if dietary_info.get('isVegetarian'):
                dietary_labels.append("vegetarian")
            if dietary_info.get('isVegan'):
                dietary_labels.append("vegan")
            if dietary_info.get('isGlutenFree'):
                dietary_labels.append("gluten-free")
            if dietary_info.get('isDairyFree'):
                dietary_labels.append("dairy-free")
            if dietary_info.get('isKeto'):
                dietary_labels.append("keto")
            if dietary_info.get('isPaleo'):
                dietary_labels.append("paleo")
            
            if dietary_labels:
                text_parts.append(f"Dietary: {', '.join(dietary_labels)}")
        
        # Add allergies information
        allergies = recipe.get('allergies', [])
        if allergies and isinstance(allergies, list):
            text_parts.append(f"Allergen-free: {', '.join(allergies)}")
        
        return ". ".join(filter(None, text_parts))

# Global instance (loaded once at startup)
embedding_service = EmbeddingService()