# ADR-004: Choose Sentence Transformers with pgvector - Semantic Search Engine

**Status:** Accepted

**Context:**  
The FitRecipes system requires an intelligent search capability that understands user intent beyond simple keyword matching. Traditional full-text search cannot handle semantic queries like "quick healthy dinner under 30 minutes" or understand that "chicken breast" is related to "poultry" and "protein." The solution must:
- Understand natural language queries and extract filters automatically (time constraints, difficulty, dietary requirements, cuisine types)
- Provide semantic search that matches meaning rather than exact keywords
- Scale efficiently with the recipe database (1000+ recipes initially, growing to 10,000+)
- Integrate seamlessly with the existing PostgreSQL/Supabase stack
- Support real-time search with acceptable latency (<3 seconds for complex queries)
- Enable ingredient-based search for users with specific items in their kitchen

**Decision:**  
We chose **Sentence Transformers** (`all-MiniLM-L6-v2` model) for semantic embeddings combined with **pgvector** extension on PostgreSQL for vector similarity search. The implementation includes:

1. **Sentence Transformers Model**: `all-MiniLM-L6-v2` (384-dimension embeddings)
   - Lightweight and fast inference (~50ms per query)
   - Multilingual support (English + Thai)
   - Pre-trained on 1B+ sentence pairs for general-domain semantic understanding
   - Balance between accuracy and performance for production use

2. **pgvector Extension**: Native PostgreSQL vector storage and similarity search
   - Cosine similarity search directly in the database
   - Efficient indexing with HNSW (Hierarchical Navigable Small World)
   - No additional infrastructure required (uses existing Supabase PostgreSQL)
   - Seamless integration with existing relational queries and filters

3. **NLP Query Parser**: Custom regex-based natural language understanding
   - Extracts time constraints ("under 30 minutes" → `maxPrepTime: 30`)
   - Identifies difficulty levels ("easy", "quick" → `difficulty: EASY`)
   - Detects dietary requirements (vegan, gluten-free, keto, etc.)
   - Recognizes cuisine types (Thai, Italian, Japanese, etc.) and meal types (breakfast, lunch, dinner)
   - Expands queries with culinary synonyms (60+ terms: "chicken" → "poultry", "hot" → "spicy")

4. **Dual Search Modes**:
   - **Smart Search** (`/search/smart`): NLP + vector embeddings for general queries (2-4s latency)
   - **Ingredient Search** (`/search/ingredients`): Direct ingredient matching for speed (0.6-0.9s latency, 6-7x faster)

5. **Hybrid Ranking System**:
   - Vector similarity score (60%)
   - User ratings (40%)
   - Multi-query expansion for improved recall

**Alternatives Considered:**

| Solution | Pros | Cons | Why Not Chosen |
|----------|------|------|----------------|
| **OpenAI Embeddings API** | High accuracy, 1536-dim vectors | $0.0001/1K tokens, API dependency, latency | Ongoing cost, external API risk, overkill for recipe search |
| **Elasticsearch** | Mature, full-text + vector hybrid | Requires separate infrastructure, complex setup | Additional server costs, operational complexity |
| **Pinecone / Weaviate** | Managed vector DB, scalable | Vendor lock-in, limited free tier | Unnecessary for current scale, adds dependency |
| **ChromaDB / FAISS** | Fast in-memory search | Requires separate persistence layer | Adds complexity, doesn't leverage existing PostgreSQL |
| **spaCy NER** | Advanced NLP, entity recognition | Heavyweight (100+ MB models), slower inference | Overkill for filter extraction, regex sufficient for v1 |

**Consequences:**

✅ **Positive:**
1. **Zero Additional Infrastructure**: Runs entirely on existing Supabase PostgreSQL + Python API
2. **Cost-Effective**: No per-request API fees, only hosting costs (~$0-7/month on Render/Railway)
3. **Low Latency**: 
   - Embedding generation: ~50ms
   - Vector search: ~100-200ms (with pgvector HNSW index)
   - Total: 2-4s for NLP Smart Search, <1s for Ingredient Search
4. **Semantic Understanding**: Users can search with natural language ("easy vegan thai dinner") instead of exact keywords
5. **Automatic Filter Extraction**: Reduces frontend complexity, improves UX
6. **Dual Modes**: Flexibility for both conversational and structured search UIs
7. **Offline Capability**: Models run locally, no external API dependency
8. **Multilingual Ready**: Model supports both English and Thai out of the box

⚠️ **Negative:**
1. **Cold Start on Free Tier**: First request after 15 minutes idle takes ~30-50 seconds (Render.com free tier)
   - Mitigation: Use uptime monitors (cron-job.org) to ping every 10 minutes, or upgrade to paid tier ($7/mo)
2. **Model Size**: 80MB model + 200MB Python dependencies increases Docker image size
   - Mitigation: Use multi-stage builds, exclude test/dev dependencies in production
3. **Memory Requirements**: 512MB RAM minimum for model inference
   - Mitigation: Render/Railway free tiers provide 512MB, sufficient for current scale
4. **Limited to 384 Dimensions**: Lower accuracy than OpenAI's 1536-dim embeddings
   - Acceptable tradeoff: Recipe search doesn't require state-of-the-art embeddings
5. **NLP Parser Limitations**: Regex-based, may miss complex/ambiguous queries
   - Future improvement: Upgrade to spaCy NER or fine-tuned transformers if needed

🔧 **Implementation Details:**
- **Embedding Generation**: Batch script (`scripts/generate_embeddings.py`) for initial corpus
- **Real-time Embeddings**: On-demand via `/v1/embeddings` endpoint for new recipes
- **Database Schema**: 
  ```sql
  CREATE EXTENSION vector;
  ALTER TABLE recipes ADD COLUMN embedding vector(384);
  CREATE INDEX ON recipes USING hnsw (embedding vector_cosine_ops);
  ```
- **API Endpoints**:
  - `POST /search/smart` - NLP + vector search
  - `POST /search/vector` - Direct vector search (no NLP)
  - `POST /search/ingredients` - Ingredient-based search
  - `POST /search/suggestions` - Autocomplete for search bar
  - `POST /ingredients/suggestions` - Autocomplete for ingredient picker
  - `POST /v1/embeddings` - Generate embeddings for new content

📊 **Performance Benchmarks:**
- Smart Search: 2-4 seconds (NLP parsing + embedding + vector search + ranking)
- Ingredient Search: 0.6-0.9 seconds (direct SQL query, no embeddings)
- Embedding Generation: ~50ms per recipe
- Cold Start (Render free): 30-50 seconds
- Concurrent Requests: 10-20 req/s on 512MB instance

🔄 **Future Enhancements:**
1. Fine-tune embeddings on recipe-specific corpus for better domain accuracy
2. Add image embeddings (CLIP model) for visual recipe search
3. Implement caching layer (Redis) for frequently searched queries
4. Upgrade to larger model (384-dim → 768-dim) if accuracy becomes critical
5. Add A/B testing framework to compare search modes

**Decision Date:** 29 October 2025  
**Author:** Easy Going
