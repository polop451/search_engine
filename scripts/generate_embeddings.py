"""
One-time script to generate embeddings for all approved recipes
Run this after initial setup or when migrating existing recipes
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import get_db_connection, get_db_cursor
from app.embeddings import embedding_service
from app.config import settings

def generate_all_embeddings():
    """Generate embeddings for all approved recipes without embeddings"""
    print("🚀 Starting embedding generation for all approved recipes...")
    
    with get_db_connection() as conn:
        with get_db_cursor(conn) as cur:
            # Fetch all approved recipes without embeddings
            # Using 'recipes' table (Prisma @@map)
            cur.execute("""
                SELECT 
                    id, title, description, "mainIngredient",
                    ingredients, "cuisineType", "dietaryInfo", "mealType", allergies
                FROM recipes 
                WHERE status = 'APPROVED' AND embedding IS NULL
                ORDER BY "createdAt" DESC
            """)
            
            recipes = cur.fetchall()
            total = len(recipes)
            
            if total == 0:
                print("✅ No recipes need embedding generation")
                return
            
            print(f"📊 Found {total} recipes to process")
            
            # Process in batches for efficiency
            batch_size = 10
            for i in range(0, total, batch_size):
                batch = recipes[i:i + batch_size]
                
                # Prepare texts for batch processing
                texts = [
                    embedding_service.prepare_recipe_text(dict(recipe))
                    for recipe in batch
                ]
                
                # Generate embeddings in batch
                embeddings = embedding_service.generate_embeddings_batch(texts)
                
                # Update database - using 'recipes' table
                for recipe, embedding in zip(batch, embeddings):
                    with conn.cursor() as update_cur:
                        update_cur.execute("""
                            UPDATE recipes 
                            SET embedding = %s::vector 
                            WHERE id = %s
                        """, (embedding, recipe['id']))
                    
                    conn.commit()
                    print(f"✅ [{i+len(batch)}/{total}] Generated embedding for: {recipe['title']}")
            
            print(f"🎉 Completed! Generated embeddings for {total} recipes")

if __name__ == "__main__":
    generate_all_embeddings()