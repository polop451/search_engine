"""
Natural Language Query Parser
Extracts structured filters from conversational queries
"""
import re
from typing import Dict, Any, List, Optional

try:
    from nltk.corpus import wordnet
    import nltk
    # Download WordNet data if not already present
    try:
        wordnet.synsets('test')
    except LookupError:
        nltk.download('wordnet', quiet=True)
        nltk.download('omw-1.4', quiet=True)
    WORDNET_AVAILABLE = True
except ImportError:
    WORDNET_AVAILABLE = False
    print("⚠️  NLTK WordNet not available. Using basic synonyms only.")


def parse_natural_language_query(query: str) -> Dict[str, Any]:
    """
    Parse natural language query into structured filters
    
    Args:
        query: User's natural language query
        
    Returns:
        Dictionary with cleaned query and extracted filters
        
    Examples:
        Input: "quick vegan thai dinner under 30 minutes"
        Output: {
            'query': 'vegan thai dinner',
            'filters': {
                'maxPrepTime': 30,
                'mealType': ['DINNER'],
                'cuisineType': 'Thai',
                'difficulty': ['EASY']
            },
            'dietaryInfo': {'isVegan': True}
        }
    """
    query_lower = query.lower()
    filters = {}
    dietary_info = {}
    
    # 1. Extract max time
    time_match = re.search(r'(?:in|within|under|less than)\s+(\d+)\s+(?:min|minutes?)', query_lower)
    if time_match:
        filters['maxPrepTime'] = int(time_match.group(1))
        filters['difficulty'] = ['EASY']  # Quick implies easy
    elif re.search(r'\b(?:quick|fast|easy)\b', query_lower):
        filters['maxPrepTime'] = 30
        filters['difficulty'] = ['EASY']
    
    # 2. Extract difficulty (if not already set by time)
    if 'difficulty' not in filters:
        if re.search(r'\b(?:easy|simple|beginner)\b', query_lower):
            filters['difficulty'] = ['EASY']
        elif re.search(r'\b(?:medium|intermediate)\b', query_lower):
            filters['difficulty'] = ['MEDIUM']
        elif re.search(r'\b(?:hard|difficult|advanced|challenging)\b', query_lower):
            filters['difficulty'] = ['HARD']
    
    # 3. Extract dietary preferences
    dietary_patterns = {
        r'\b(?:vegan|plant-based)\b': 'isVegan',
        r'\b(?:vegetarian|meatless)\b': 'isVegetarian',
        r'\b(?:gluten-free|gluten free)\b': 'isGlutenFree',
        r'\b(?:dairy-free|dairy free|lactose free)\b': 'isDairyFree',
        r'\b(?:keto|ketogenic|low-carb)\b': 'isKeto',
        r'\b(?:paleo|paleolithic)\b': 'isPaleo',
    }
    
    for pattern, diet_key in dietary_patterns.items():
        if re.search(pattern, query_lower):
            dietary_info[diet_key] = True
    
    # 4. Extract cuisine type
    cuisine_patterns = {
        r'\b(?:thai|thailand)\b': 'Thai',
        r'\b(?:italian|italy)\b': 'Italian',
        r'\b(?:japanese|japan)\b': 'Japanese',
        r'\b(?:chinese|china)\b': 'Chinese',
        r'\b(?:mexican|mexico)\b': 'Mexican',
        r'\b(?:indian|india)\b': 'Indian',
        r'\b(?:korean|korea)\b': 'Korean',
        r'\b(?:vietnamese|vietnam)\b': 'Vietnamese',
        r'\b(?:mediterranean)\b': 'Mediterranean',
        r'\b(?:american)\b': 'American',
        r'\b(?:french|france)\b': 'French',
    }
    
    for pattern, cuisine in cuisine_patterns.items():
        if re.search(pattern, query_lower):
            filters['cuisineType'] = cuisine
            break
    
    # 5. Extract meal type
    meal_patterns = {
        r'\b(?:breakfast|morning)\b': 'BREAKFAST',
        r'\b(?:lunch|noon)\b': 'LUNCH',
        r'\b(?:dinner|evening)\b': 'DINNER',
        r'\b(?:snack|appetizer)\b': 'SNACK',
        r'\b(?:dessert|sweet)\b': 'DESSERT',
    }
    
    meal_types = []
    for pattern, meal_type in meal_patterns.items():
        if re.search(pattern, query_lower):
            meal_types.append(meal_type)
    
    if meal_types:
        filters['mealType'] = meal_types
    
    # 6. Clean query (remove filter keywords for better embedding)
    clean_query = query
    
    # Remove time expressions
    clean_query = re.sub(r'(?:in|within|under|less than)\s+\d+\s+(?:min|minutes?)', '', clean_query, flags=re.IGNORECASE)
    
    # Remove difficulty keywords
    clean_query = re.sub(r'\b(?:quick|fast|easy|simple|beginner|medium|intermediate|hard|difficult|advanced|challenging)\b', '', clean_query, flags=re.IGNORECASE)
    
    # Clean up extra spaces
    clean_query = ' '.join(clean_query.split())
    
    return {
        'query': clean_query or query,  # Fallback to original if empty
        'filters': filters,
        'dietaryInfo': dietary_info if dietary_info else None
    }


def expand_query_with_synonyms(query: str) -> List[str]:
    """
    Generate query variations with culinary synonyms
    Uses NLTK WordNet for intelligent synonym expansion if available
    
    Args:
        query: Original search query
        
    Returns:
        List of query variations including original
        
    Example:
        Input: "healthy chicken dinner"
        Output: [
            "healthy chicken dinner",
            "nutritious chicken dinner", 
            "wholesome chicken dinner",
            "healthy poultry dinner"
        ]
    """
    # Curated culinary-specific synonyms (domain knowledge)
    # These are context-aware for cooking/recipes
    culinary_synonyms = {
        # Food preparation terms
        'healthy': ['nutritious', 'wholesome', 'clean'],
        'quick': ['fast', 'rapid', 'speedy', 'swift'],
        'easy': ['simple', 'basic', 'straightforward'],
        'delicious': ['tasty', 'flavorful', 'savory'],
        'spicy': ['hot', 'fiery', 'pungent', 'zesty'],
        'mild': ['gentle', 'subtle', 'light'],
        'rich': ['creamy', 'decadent', 'indulgent'],
        'light': ['refreshing', 'crisp', 'fresh'],
        
        # Meal types
        'breakfast': ['morning meal', 'brunch'],
        'lunch': ['midday meal', 'luncheon'],
        'dinner': ['evening meal', 'supper'],
        'snack': ['appetizer', 'bite', 'nibble'],
        'dessert': ['sweet', 'treat'],
        
        # Protein sources
        'chicken': ['poultry', 'fowl'],
        'beef': ['steak', 'meat'],
        'pork': ['ham', 'bacon'],
        'fish': ['seafood'],
        'tofu': ['bean curd', 'soy'],
        
        # Dietary terms
        'vegetarian': ['plant-based', 'meatless', 'veggie'],
        'vegan': ['plant-based', 'dairy-free'],
        'low-carb': ['keto', 'ketogenic', 'low-carbohydrate'],
        'gluten-free': ['wheat-free'],
        
        # Cooking methods
        'grilled': ['barbecued', 'charred', 'broiled'],
        'fried': ['pan-fried', 'deep-fried', 'crispy'],
        'baked': ['roasted', 'oven-cooked'],
        'steamed': ['boiled', 'poached'],
        'raw': ['fresh', 'uncooked'],
        
        # Textures
        'crispy': ['crunchy', 'crisp'],
        'creamy': ['smooth', 'velvety'],
        'tender': ['soft', 'juicy'],
        'chewy': ['firm', 'dense'],
    }
    
    words = query.lower().split()
    expanded_queries = [query]  # Original query always first
    
    # Method 1: Use curated culinary synonyms (always available)
    for word in words:
        if word in culinary_synonyms:
            for synonym in culinary_synonyms[word][:2]:  # Limit to top 2 per word
                variant = query.lower().replace(word, synonym)
                if variant not in expanded_queries and variant != query.lower():
                    expanded_queries.append(variant)
                    if len(expanded_queries) >= 5:
                        break
    
    # Method 2: Use WordNet for additional intelligent synonyms (if available)
    if WORDNET_AVAILABLE and len(expanded_queries) < 5:
        for word in words:
            if len(word) < 4 or word in culinary_synonyms:
                continue  # Skip short words and already processed words
            
            # Get synsets (synonym sets) for the word
            synsets = wordnet.synsets(word, pos=wordnet.NOUN)  # Focus on nouns for cooking
            if not synsets:
                synsets = wordnet.synsets(word, pos=wordnet.ADJ)  # Then adjectives
            
            for synset in synsets[:2]:  # Top 2 most common meanings
                # Get lemmas (actual word forms)
                for lemma in synset.lemmas()[:2]:
                    synonym = lemma.name().replace('_', ' ')
                    
                    # Skip if same word or too different
                    if synonym.lower() == word or len(synonym) < 3:
                        continue
                    
                    # Check semantic similarity (basic filter)
                    if any(char.isdigit() for char in synonym):
                        continue  # Skip if contains numbers
                    
                    variant = query.lower().replace(word, synonym)
                    if variant not in expanded_queries and variant != query.lower():
                        expanded_queries.append(variant)
                        if len(expanded_queries) >= 5:
                            break
                
                if len(expanded_queries) >= 5:
                    break
            
            if len(expanded_queries) >= 5:
                break
    
    return expanded_queries[:5]  # Maximum 5 variations to avoid overfit
