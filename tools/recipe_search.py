"""
Recipe Search Tool
Filterable local search over recipe dataset with support for ingredients, dietary restrictions, cuisine, time, and difficulty
"""

import json
import logging
import os
from typing import List, Dict, Any, Optional

from config import Config

logger = logging.getLogger(__name__)


class RecipeSearch:
    """
    Tool for searching recipes based on various filters.
    
    Searches a local JSON dataset with support for:
    - Ingredient matching
    - Dietary restrictions (vegetarian, vegan, gluten-free, etc.)
    - Cuisine type (Italian, Mexican, Asian, etc.)
    - Maximum cooking time
    - Difficulty level
    
    Extensibility:
    This tool is designed with a clean interface for future integration with
    external recipe APIs like Spoonacular, Edamam, or TheMealDB.
    
    To integrate an external API:
    1. Create a new class inheriting from RecipeSearchInterface
    2. Implement _fetch_recipes() to call the API
    3. Update the factory/configuration to use the new implementation
    """
    
    # OpenAI function schema for orchestrator
    schema = {
        "type": "function",
        "function": {
            "name": "recipe_search",
            "description": "Search for recipes based on ingredients, dietary restrictions, cuisine, cooking time, and difficulty level. Returns matching recipes with details.",
            "parameters": {
                "type": "object",
                "properties": {
                    "ingredients": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of ingredients to search for (optional)"
                    },
                    "dietary_restrictions": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Dietary constraints like 'vegetarian', 'vegan', 'gluten-free', 'dairy-free' (optional)"
                    },
                    "cuisine": {
                        "type": "string",
                        "description": "Cuisine type like 'Italian', 'Mexican', 'Asian', 'Mediterranean' (optional)"
                    },
                    "max_time_minutes": {
                        "type": "integer",
                        "description": "Maximum cooking time in minutes (optional)"
                    },
                    "difficulty": {
                        "type": "string",
                        "enum": ["easy", "medium", "hard"],
                        "description": "Recipe difficulty level (optional)"
                    }
                },
                "required": []
            }
        }
    }
    
    def __init__(self, data_path: str = None):
        """
        Initialize the recipe search tool.
        
        Args:
            data_path: Path to recipe JSON file (default from config)
        """
        self.data_path = data_path or Config.RECIPE_DATA_PATH
        self.recipes = self._load_recipes()
        
        logger.info(f"RecipeSearch initialized with {len(self.recipes)} recipes")
    
    def _load_recipes(self) -> List[Dict[str, Any]]:
        """Load recipes from JSON file"""
        try:
            if not os.path.exists(self.data_path):
                logger.warning(f"Recipe data file not found: {self.data_path}")
                return []
            
            with open(self.data_path, 'r', encoding='utf-8') as f:
                recipes = json.load(f)
            
            logger.info(f"Loaded {len(recipes)} recipes from {self.data_path}")
            return recipes
            
        except Exception as e:
            logger.error(f"Error loading recipes: {str(e)}")
            return []
    
    def search(
        self,
        ingredients: Optional[List[str]] = None,
        dietary_restrictions: Optional[List[str]] = None,
        cuisine: Optional[str] = None,
        max_time_minutes: Optional[int] = None,
        difficulty: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Search recipes with multiple filters.
        
        Args:
            ingredients: List of ingredients to match
            dietary_restrictions: Dietary constraints to filter by
            cuisine: Cuisine type to filter by
            max_time_minutes: Maximum cooking time
            difficulty: Recipe difficulty level
            
        Returns:
            Dict with:
                - recipes: List of matching recipes
                - count: Number of matches
                - filters_applied: Summary of filters used
        """
        
        logger.info(f"Searching recipes with filters: ingredients={ingredients}, "
                   f"dietary={dietary_restrictions}, cuisine={cuisine}, "
                   f"max_time={max_time_minutes}, difficulty={difficulty}")
        
        filtered_recipes = self.recipes.copy()
        filters_applied = []
        
        # Filter by ingredients
        if ingredients:
            filtered_recipes = [
                recipe for recipe in filtered_recipes
                if self._matches_ingredients(recipe, ingredients)
            ]
            filters_applied.append(f"ingredients: {', '.join(ingredients)}")
        
        # Filter by dietary restrictions
        if dietary_restrictions:
            for restriction in dietary_restrictions:
                filtered_recipes = [
                    recipe for recipe in filtered_recipes
                    if self._matches_dietary(recipe, restriction)
                ]
            filters_applied.append(f"dietary: {', '.join(dietary_restrictions)}")
        
        # Filter by cuisine
        if cuisine:
            filtered_recipes = [
                recipe for recipe in filtered_recipes
                if recipe.get('cuisine', '').lower() == cuisine.lower()
            ]
            filters_applied.append(f"cuisine: {cuisine}")
        
        # Filter by max cooking time
        if max_time_minutes:
            filtered_recipes = [
                recipe for recipe in filtered_recipes
                if recipe.get('time_minutes', 999) <= max_time_minutes
            ]
            filters_applied.append(f"max time: {max_time_minutes} minutes")
        
        # Filter by difficulty
        if difficulty:
            filtered_recipes = [
                recipe for recipe in filtered_recipes
                if recipe.get('difficulty', '').lower() == difficulty.lower()
            ]
            filters_applied.append(f"difficulty: {difficulty}")
        
        # Limit results
        limited_recipes = filtered_recipes[:Config.MAX_RECIPE_RESULTS]
        
        # Format results for readability
        formatted_recipes = [
            self._format_recipe_summary(recipe) for recipe in limited_recipes
        ]
        
        result = {
            "recipes": formatted_recipes,
            "count": len(filtered_recipes),
            "returned": len(limited_recipes),
            "filters_applied": filters_applied if filters_applied else ["none"]
        }
        
        logger.info(f"Search returned {len(limited_recipes)} of {len(filtered_recipes)} matching recipes")
        
        return result
    
    def _matches_ingredients(self, recipe: Dict, search_ingredients: List[str]) -> bool:
        """Check if recipe contains any of the search ingredients"""
        recipe_ingredients = [ing.lower() for ing in recipe.get('ingredients', [])]
        
        # Match if any search ingredient appears in recipe ingredients
        for search_ing in search_ingredients:
            search_ing_lower = search_ing.lower()
            for recipe_ing in recipe_ingredients:
                if search_ing_lower in recipe_ing or recipe_ing in search_ing_lower:
                    return True
        
        return False
    
    def _matches_dietary(self, recipe: Dict, restriction: str) -> bool:
        """Check if recipe matches dietary restriction"""
        recipe_diets = [diet.lower() for diet in recipe.get('dietary_info', [])]
        return restriction.lower() in recipe_diets
    
    def _format_recipe_summary(self, recipe: Dict) -> Dict[str, Any]:
        """Format recipe for concise display"""
        return {
            "title": recipe.get('title', 'Untitled'),
            "description": recipe.get('description', ''),
            "cuisine": recipe.get('cuisine', 'Unknown'),
            "time_minutes": recipe.get('time_minutes', 0),
            "difficulty": recipe.get('difficulty', 'medium'),
            "dietary_info": recipe.get('dietary_info', []),
            "main_ingredients": recipe.get('ingredients', [])[:5],  # First 5 ingredients
            "servings": recipe.get('servings', 4)
        }


# Create callable instance for orchestrator
def recipe_search(
    ingredients: Optional[List[str]] = None,
    dietary_restrictions: Optional[List[str]] = None,
    cuisine: Optional[str] = None,
    max_time_minutes: Optional[int] = None,
    difficulty: Optional[str] = None
) -> Dict[str, Any]:
    """
    Callable wrapper for the recipe search tool.
    
    Args:
        ingredients: List of ingredients to match (optional)
        dietary_restrictions: Dietary constraints (optional)
        cuisine: Cuisine type (optional)
        max_time_minutes: Maximum cooking time (optional)
        difficulty: Recipe difficulty (optional)
        
    Returns:
        Search results with matching recipes
        
    Extensibility - External API Integration:
    To replace local search with an external API (e.g., Spoonacular):
    
    1. Get API key and add to config.py:
       SPOONACULAR_API_KEY = os.getenv("SPOONACULAR_API_KEY")
    
    2. Replace the search logic:
       import requests
       
       def recipe_search(...):
           api_key = Config.SPOONACULAR_API_KEY
           url = "https://api.spoonacular.com/recipes/complexSearch"
           
           params = {
               "apiKey": api_key,
               "includeIngredients": ",".join(ingredients) if ingredients else None,
               "diet": dietary_restrictions[0] if dietary_restrictions else None,
               "cuisine": cuisine,
               "maxReadyTime": max_time_minutes,
               # ... other params
           }
           
           response = requests.get(url, params=params)
           data = response.json()
           
           # Transform API response to match our format
           return format_api_results(data)
    
    3. Keep the same return format for compatibility with orchestrator
    """
    searcher = RecipeSearch()
    return searcher.search(
        ingredients=ingredients,
        dietary_restrictions=dietary_restrictions,
        cuisine=cuisine,
        max_time_minutes=max_time_minutes,
        difficulty=difficulty
    )


# Attach schema to function for orchestrator
recipe_search.schema = RecipeSearch.schema


if __name__ == "__main__":
    # Test the search
    logging.basicConfig(level=logging.INFO)
    
    print("\n" + "="*60)
    print("Testing Recipe Search Tool")
    print("="*60)
    
    # Test cases
    test_cases = [
        {
            "name": "Vegetarian pasta",
            "params": {"dietary_restrictions": ["vegetarian"], "cuisine": "Italian"}
        },
        {
            "name": "Quick recipes under 30 min",
            "params": {"max_time_minutes": 30}
        },
        {
            "name": "Easy chicken recipes",
            "params": {"ingredients": ["chicken"], "difficulty": "easy"}
        }
    ]
    
    searcher = RecipeSearch()
    
    for test in test_cases:
        print(f"\n{'='*60}")
        print(f"Test: {test['name']}")
        print(f"Params: {test['params']}")
        result = searcher.search(**test['params'])
        print(f"Found: {result['count']} recipes")
        print(f"Filters: {result['filters_applied']}")
        if result['recipes']:
            print(f"First result: {result['recipes'][0]['title']}")
