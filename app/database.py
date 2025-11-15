import psycopg2
from psycopg2.extras import RealDictCursor
from pgvector.psycopg2 import register_vector
from contextlib import contextmanager
from app.config import settings

@contextmanager
def get_db_connection():
    """Context manager for database connections with pgvector support"""
    conn = psycopg2.connect(settings.database_url)
    register_vector(conn)
    try:
        yield conn
    finally:
        conn.close()

def get_db_cursor(conn):
    """Get a cursor with RealDictCursor for dict-like results"""
    return conn.cursor(cursor_factory=RealDictCursor)

def init_db():
    """Initialize database with pgvector extension and indexes"""
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            # Enable pgvector extension
            cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
            
            # Check if embedding column exists in recipes table (Prisma @@map)
            cur.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'recipes'
                AND column_name = 'embedding';
            """)
            
            if not cur.fetchone():
                print("📦 Adding embedding column to recipes table...")
                # Add embedding column to recipes table
                cur.execute(f"""
                    ALTER TABLE recipes 
                    ADD COLUMN embedding vector({settings.embedding_dimension});
                """)
                
                # Create index for vector similarity search (IVFFlat algorithm)
                cur.execute("""
                    CREATE INDEX IF NOT EXISTS recipes_embedding_idx 
                    ON recipes 
                    USING ivfflat (embedding vector_cosine_ops)
                    WITH (lists = 100);
                """)
                
                print("✅ Embedding column and index created")
            else:
                print("✅ Embedding column already exists")
            
            conn.commit()
            print("✅ Database initialized with pgvector support")