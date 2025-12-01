"""
Ingredient Extractor Tool
NER-style parsing with regex patterns and LLM fallback for ingredient extraction
"""

import re
import logging
from typing import List, Dict, Any
from openai import AzureOpenAI

from config import Config

logger = logging.getLogger(__name__)


# Common units and measurements
UNITS = [
    "cup", "cups", "tablespoon", "tablespoons", "tbsp", "teaspoon", "teaspoons", "tsp",
    "ounce", "ounces", "oz", "pound", "pounds", "lb", "lbs", "gram", "grams", "g",
    "kilogram", "kilograms", "kg", "milliliter", "milliliters", "ml", "liter", "liters", "l",
    "pinch", "dash", "handful", "slice", "slices", "piece", "pieces", "clove", "cloves"
]

# Common dietary keywords
DIETARY_KEYWORDS = {
    "vegetarian": ["vegetarian", "veggie"],
    "vegan": ["vegan", "plant-based", "plant based"],
    "gluten-free": ["gluten-free", "gluten free", "no gluten", "celiac"],
    "dairy-free": ["dairy-free", "dairy free", "lactose-free", "no dairy", "no milk"],
    "nut-free": ["nut-free", "nut free", "no nuts"],
    "low-carb": ["low-carb", "low carb", "keto", "ketogenic"],
    "paleo": ["paleo", "paleolithic"],
    "halal": ["halal"],
    "kosher": ["kosher"]
}


class IngredientExtractor:
    """
    Tool for extracting ingredients, quantities, and dietary constraints from text.
    
    Strategy:
    1. First try regex-based extraction (fast, deterministic)
    2. Fall back to LLM-based extraction for complex cases
    3. Extract dietary constraints separately
    """
    
    # OpenAI function schema for orchestrator
    schema = {
        "type": "function",
        "function": {
            "name": "ingredient_extractor",
            "description": "Extract ingredients, quantities, and dietary constraints from user text. Use when user mentions ingredients they have or provides recipe text to parse.",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "The text containing ingredients to extract"
                    }
                },
                "required": ["text"]
            }
        }
    }
    
    def __init__(self):
        """Initialize the ingredient extractor"""
        self.client = AzureOpenAI(**Config.get_azure_client_config())
        self.model = Config.MODEL_DEPLOYMENT_NAME
        
        # Build regex pattern for units
        units_pattern = "|".join([re.escape(unit) for unit in UNITS])
        
        # Pattern: optional number/fraction + optional unit + ingredient name
        # Examples: "2 cups flour", "3 eggs", "1/2 tsp salt", "tomatoes"
        self.ingredient_pattern = re.compile(
            rf'(\d+(?:[./]\d+)?)\s*({units_pattern})?\s+([a-zA-Z\s,]+)',
            re.IGNORECASE
        )
        
        logger.info("IngredientExtractor initialized")
    
    def extract(self, text: str) -> Dict[str, Any]:
        """
        Main extraction method.
        
        Args:
            text: Input text containing ingredients
            
        Returns:
            Dict with:
                - ingredients: List of parsed ingredients
                - dietary_constraints: List of detected dietary restrictions
                - raw_text: Original input for reference
        """
        
        logger.info(f"Extracting ingredients from: {text[:100]}...")
        
        # Try regex extraction first
        regex_ingredients = self._regex_extract(text)
        
        # Extract dietary constraints
        dietary_constraints = self._extract_dietary_constraints(text)
        
        # If regex found ingredients, use them; otherwise fall back to LLM
        if regex_ingredients:
            logger.info(f"Regex extraction found {len(regex_ingredients)} ingredients")
            ingredients = regex_ingredients
        else:
            logger.info("Regex extraction failed, falling back to LLM")
            ingredients = self._llm_extract(text)
        
        result = {
            "ingredients": ingredients,
            "dietary_constraints": dietary_constraints,
            "raw_text": text,
            "count": len(ingredients)
        }
        
        logger.info(f"Extraction result: {len(ingredients)} ingredients, {len(dietary_constraints)} constraints")
        
        return result
    
    def _regex_extract(self, text: str) -> List[Dict[str, str]]:
        """
        Extract ingredients using regex patterns.
        
        Returns:
            List of ingredient dicts with quantity, unit, and name
        """
        
        ingredients = []
        
        # Find all ingredient-like patterns
        matches = self.ingredient_pattern.findall(text)
        
        for match in matches:
            quantity, unit, name = match
            
            ingredient = {
                "name": name.strip().lower(),
                "quantity": quantity.strip() if quantity else "",
                "unit": unit.strip().lower() if unit else ""
            }
            
            ingredients.append(ingredient)
        
        # Also try to find simple ingredient names without quantities
        # Split by common separators
        for separator in [',', ';', '\n', ' and ', ' or ']:
            if separator in text.lower():
                parts = text.lower().split(separator)
                for part in parts:
                    part = part.strip()
                    # Check if it's a simple ingredient name (not already captured)
                    if part and len(part.split()) <= 3:
                        # Avoid duplicates
                        if not any(ing['name'] == part for ing in ingredients):
                            # Check if it doesn't contain numbers (likely a plain ingredient)
                            if not re.search(r'\d', part):
                                ingredients.append({
                                    "name": part,
                                    "quantity": "",
                                    "unit": ""
                                })
        
        return ingredients
    
    def _llm_extract(self, text: str) -> List[Dict[str, str]]:
        """
        Extract ingredients using LLM as fallback.
        
        Returns:
            List of ingredient dicts
        """
        
        try:
            prompt = f"""Extract all ingredients from the following text. For each ingredient, identify:
- name: the ingredient name
- quantity: the amount (if specified)
- unit: the measurement unit (if specified)

Return the result as a JSON list. If no ingredients are found, return an empty list.

Text: {text}

Respond with ONLY a JSON list, no other text."""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a precise ingredient extraction assistant. Respond only with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            result_text = response.choices[0].message.content.strip()
            
            # Try to parse JSON response
            import json
            ingredients = json.loads(result_text)
            
            return ingredients if isinstance(ingredients, list) else []
            
        except Exception as e:
            logger.error(f"LLM extraction failed: {str(e)}")
            return []
    
    def _extract_dietary_constraints(self, text: str) -> List[str]:
        """
        Extract dietary constraints/restrictions from text.
        
        Returns:
            List of detected dietary restrictions
        """
        
        text_lower = text.lower()
        constraints = []
        
        for constraint, keywords in DIETARY_KEYWORDS.items():
            for keyword in keywords:
                if keyword in text_lower:
                    if constraint not in constraints:
                        constraints.append(constraint)
                    break
        
        return constraints


# Create callable instance for orchestrator
def ingredient_extractor(text: str) -> Dict[str, Any]:
    """
    Callable wrapper for the ingredient extractor tool.
    
    Args:
        text: Text containing ingredients to extract
        
    Returns:
        Extraction results with ingredients and dietary constraints
    """
    extractor = IngredientExtractor()
    return extractor.extract(text)


# Attach schema to function for orchestrator
ingredient_extractor.schema = IngredientExtractor.schema


if __name__ == "__main__":
    # Test the extractor
    logging.basicConfig(level=logging.INFO)
    
    test_cases = [
        "I have 2 cups flour, 3 eggs, 1/2 cup sugar, and butter",
        "tomatoes, basil, mozzarella cheese, olive oil",
        "Find me a vegan gluten-free recipe with chickpeas and spinach",
        "I need a dairy-free recipe for salmon, lemon, and asparagus"
    ]
    
    extractor = IngredientExtractor()
    
    for test_text in test_cases:
        print(f"\n{'='*60}")
        print(f"Input: {test_text}")
        result = extractor.extract(test_text)
        print(f"Ingredients: {result['ingredients']}")
        print(f"Dietary: {result['dietary_constraints']}")
