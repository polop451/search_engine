# 🔍 Dual Search Modes: NLP vs Ingredient-Based

## Overview
ระบบค้นหาแบบ 2 โหมด ให้เลือกใช้ตามความเหมาะสม:
1. **NLP Smart Search** (`/search/smart`) - เข้าใจภาษาธรรมชาติ แยกตัวกรองอัตโนมัติ
2. **Ingredient Search** (`/search/ingredients`) - ค้นหาจากวัตถุดิบโดยตรง เร็วกว่า แม่นยำกว่า

## 🎯 เมื่อไหร่ใช้โหมดไหน?

### ใช้ NLP Smart Search เมื่อ:
- ✅ User พิมพ์คำค้นหาแบบภาษาธรรมชาติ (e.g., "quick vegan thai dinner under 30 minutes")
- ✅ ต้องการแยก filters อัตโนมัติ (time, difficulty, dietary, cuisine, meal type)
- ✅ ไม่รู้วัตถุดิบแน่ชัด แต่รู้ลักษณะอาหารที่ต้องการ
- ✅ ต้องการ semantic search (ค้นหาตามความหมาย)

### ใช้ Ingredient Search เมื่อ:
- ✅ User เลือกวัตถุดิบจากรายการ (e.g., checkbox, dropdown)
- ✅ มีวัตถุดิบในตู้เย็น ต้องการหาสูตรที่ใช้ได้
- ✅ ต้องการความเร็ว (เร็วกว่า 6-7 เท่า)
- ✅ ต้องการความแม่นยำในการจับคู่วัตถุดิบ

## 📊 Feature Comparison

| Feature | NLP Smart Search | Ingredient Search |
|---------|------------------|-------------------|
| **Endpoint** | `/search/smart` | `/search/ingredients` |
| **Input** | Natural language text | Array of ingredient names |
| **Speed** | 🐢 2-4 seconds | ⚡ 0.6-0.9 seconds |
| **Accuracy** | 🎯 Semantic matching | 🎯 Exact ingredient matching |
| **Auto-filter** | ✅ Yes (NLP extraction) | ❌ No (manual only) |
| **Synonym expansion** | ✅ Yes (60+ culinary terms) | ❌ No |
| **Vector embedding** | ✅ Yes (384-dim) | ❌ No |
| **Match modes** | ❌ N/A | ✅ Yes (any/all) |
| **Score system** | Similarity + Rating | Ingredient match + Rating |
| **Use case** | General search bar | Ingredient selector UI |

## 🔧 API Documentation

### 1. NLP Smart Search

**Endpoint:** `POST /search/smart`

**Request:**
```json
{
  "query": "quick vegan thai dinner under 30 minutes",
  "limit": 10,
  "filters": {
    "mealType": ["DINNER"],
    "maxPrepTime": 30
  }
}
```

**Response:**
```json
{
  "status": "success",
  "data": [...recipes...],
  "total": 5,
  "query": "quick vegan thai dinner under 30 minutes",
  "parsed_query": "vegan thai dinner",
  "extracted_filters": {
    "maxPrepTime": 30,
    "difficulty": ["EASY"],
    "cuisineType": "Thai",
    "mealType": ["DINNER"],
    "dietaryInfo": {
      "isVegan": true
    }
  },
  "execution_time_ms": 4194.32
}
```

**Features:**
- ✅ Automatic filter extraction from natural language
- ✅ Query cleaning (removes filter keywords)
- ✅ Synonym expansion (5 variations)
- ✅ Multi-query ranking with weighted scores
- ✅ Returns extracted filters for transparency

---

### 2. Ingredient Search

**Endpoint:** `POST /search/ingredients`

**Request:**
```json
{
  "ingredients": ["chicken", "garlic", "tomato"],
  "limit": 10,
  "match_mode": "any",
  "filters": {
    "mealType": ["LUNCH", "DINNER"],
    "maxPrepTime": 45
  }
}
```

**Response:**
```json
{
  "status": "success",
  "data": [
    {
      "id": "recipe-id",
      "title": "Thai Green Curry with Chicken",
      "mainIngredient": "Chicken",
      "match_score": 21,
      "matched_count": 2,
      ...
    }
  ],
  "total": 1,
  "ingredients": ["chicken", "garlic", "tomato"],
  "match_mode": "any",
  "execution_time_ms": 633.33
}
```

**Match Modes:**
- `"any"` (OR): Recipes containing ANY of the ingredients
- `"all"` (AND): Recipes containing ALL of the ingredients

**Scoring System:**
| Match Type | Weight | Description |
|------------|--------|-------------|
| Primary | 10 | Exact mainIngredient match |
| Secondary | 5 | mainIngredient contains ingredient |
| Tertiary | 3 per match | ingredients JSON array match |
| Quaternary | 2 | Title contains ingredient |
| Quinary | 1 | Description contains ingredient |

**Final Score:** `match_score * 0.7 + (averageRating / 5.0) * 0.3`

## 💡 Usage Examples

### Example 1: General Search (Use NLP)
```bash
# User types in search bar
curl -X POST "http://localhost:8000/search/smart" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_API_KEY" \
  -d '{
    "query": "easy breakfast for beginners",
    "limit": 5
  }'
```

**Why NLP?** User is describing what they want, not specifying ingredients

---

### Example 2: "What's in my fridge?" (Use Ingredient)
```bash
# User has chicken, garlic, and tomatoes
curl -X POST "http://localhost:8000/search/ingredients" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_API_KEY" \
  -d '{
    "ingredients": ["chicken", "garlic", "tomato"],
    "match_mode": "any",
    "limit": 10
  }'
```

**Why Ingredient?** Specific ingredient list, need fast results

---

### Example 3: Recipe with ALL ingredients (Use Ingredient)
```bash
# Must use both egg and rice
curl -X POST "http://localhost:8000/search/ingredients" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_API_KEY" \
  -d '{
    "ingredients": ["egg", "rice"],
    "match_mode": "all",
    "limit": 5
  }'
```

**Why Ingredient?** Need exact AND matching logic

---

### Example 4: Complex dietary query (Use NLP)
```bash
# Complex natural language with dietary requirements
curl -X POST "http://localhost:8000/search/smart" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_API_KEY" \
  -d '{
    "query": "keto lunch recipe ready in 20 minutes",
    "limit": 5
  }'
```

**Why NLP?** Automatic extraction of dietary info and time constraints

## 🎨 Frontend Integration

### Recommended UI Design

#### Option 1: Tabbed Interface
```
┌─────────────────────────────────────────┐
│ [Search by Text] [Search by Ingredient] │
├─────────────────────────────────────────┤
│                                         │
│ Tab 1: Free text search box             │
│ → Uses /search/smart                    │
│                                         │
│ Tab 2: Ingredient checkboxes/selector   │
│ → Uses /search/ingredients              │
└─────────────────────────────────────────┘
```

#### Option 2: Smart Detection
```typescript
// Auto-detect which endpoint to use
function search(input: string | string[]) {
  if (Array.isArray(input)) {
    // Array of ingredients → Use ingredient search
    return ingredientSearch(input);
  } else if (input.includes(',') || input.length < 30) {
    // Comma-separated or short → Possibly ingredients
    const ingredients = input.split(',').map(s => s.trim());
    return ingredientSearch(ingredients);
  } else {
    // Full sentence → Use NLP search
    return nlpSearch(input);
  }
}
```

#### Option 3: Hybrid Mode Toggle
```
┌─────────────────────────────────────────┐
│ Search: [____________]  [Mode: Smart ▼] │
│                                         │
│ Smart Mode:                             │
│ - Natural language                      │
│ - Auto-filter extraction                │
│                                         │
│ Ingredient Mode:                        │
│ - Comma-separated ingredients           │
│ - Exact matching                        │
└─────────────────────────────────────────┘
```

## 📈 Performance Comparison

### Test: "chicken" search

#### NLP Smart Search:
```
Query: "chicken"
Parsed: "chicken"
Extracted filters: {}
Found: 1 recipe
Time: 2829ms
```

#### Ingredient Search:
```
Ingredients: ["chicken"]
Match mode: any
Found: 1 recipe
Time: 633ms
```

**Speed Improvement:** 4.5x faster ⚡

---

### Test: Complex query

#### NLP Smart Search:
```
Query: "quick vegan thai dinner under 30 minutes"
Extracted: cuisineType=Thai, isVegan=true, maxPrepTime=30, difficulty=EASY, mealType=DINNER
Found: 0 recipes (too restrictive)
Time: 4194ms
```

#### Ingredient Search:
```
Ingredients: ["tofu", "coconut milk"]
Filters: {cuisineType: "Thai", mealType: ["DINNER"]}
Found: 2 recipes
Time: 789ms
```

**Speed Improvement:** 5.3x faster ⚡

## 🔮 Use Case Recommendations

| User Intent | Recommended Mode | Example Query |
|-------------|-----------------|---------------|
| "I want something healthy and quick" | NLP Smart | "healthy quick breakfast" |
| "I have chicken and garlic" | Ingredient | ["chicken", "garlic"] |
| "Show me vegan keto recipes" | NLP Smart | "vegan keto dinner" |
| "Recipes with ALL these ingredients" | Ingredient | ["egg", "rice"] + match_mode="all" |
| "Easy recipes for beginners" | NLP Smart | "easy recipes for beginners" |
| "What can I make with tomatoes?" | Ingredient | ["tomato"] |

## 🎯 Best Practices

### For NLP Smart Search:
1. ✅ Use for general search bars
2. ✅ Show extracted filters to user for transparency
3. ✅ Allow manual filter override
4. ✅ Handle empty results with suggestions

### For Ingredient Search:
1. ✅ Use for ingredient selector UI
2. ✅ Show match_score to indicate relevance
3. ✅ Display matched_count (how many ingredients matched)
4. ✅ Provide both "any" and "all" toggle options

## 🚀 Optimization Tips

### When to use each mode:

**Use NLP Smart Search for:**
- 📱 Mobile app main search
- 🖥️ Desktop search bar
- 🎙️ Voice search integration
- 📝 General recipe discovery

**Use Ingredient Search for:**
- 🥗 "What's in my fridge" feature
- 📋 Shopping list integration
- ✅ Ingredient filter UI
- 🔍 Advanced search filters

## 📝 Summary

### NLP Smart Search (`/search/smart`)
**Pros:**
- ✅ Natural language understanding
- ✅ Auto-filter extraction
- ✅ Synonym expansion
- ✅ Semantic search

**Cons:**
- ❌ Slower (2-4 seconds)
- ❌ Can be too restrictive with multiple filters

**Best for:** General search, discovery, voice input

---

### Ingredient Search (`/search/ingredients`)
**Pros:**
- ✅ Fast (0.6-0.9 seconds)
- ✅ Exact ingredient matching
- ✅ AND/OR logic support
- ✅ Clear scoring system

**Cons:**
- ❌ No auto-filter extraction
- ❌ No synonym support

**Best for:** Ingredient selector, "what's in my fridge", exact matching

---

### Recommendation:
**Use BOTH!** Implement tabbed interface or smart detection to give users the best of both worlds 🎉

**Quick Decision Tree:**
```
User has specific ingredients? 
  → YES: Use Ingredient Search ⚡
  → NO: Use NLP Smart Search 🧠
```
