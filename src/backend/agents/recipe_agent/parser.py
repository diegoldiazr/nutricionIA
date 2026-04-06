"""
Recipe Parser - Pure functions for parsing recipe text from AI responses.

All functions are stateless and testable.
"""

from typing import List, Dict, Any, Optional
import re


def parse_recipe_block(text: str) -> Optional[Dict[str, Any]]:
    """
    Parse a single recipe block from text.

    Args:
        text: Raw recipe text block

    Returns:
        Structured recipe dict or None if parsing fails
    """
    lines = text.strip().split('\n')
    if not lines:
        return None

    # First line is name (strip markdown)
    name = lines[0].strip().strip('*#\'"')

    ingredients: List[str] = []
    instructions: List[str] = []
    nutrition: Dict[str, Any] = {}
    current_section = None

    for line in lines[1:]:
        line_lower = line.lower().strip()

        # Section detection
        if 'ingredient' in line_lower:
            current_section = 'ingredients'
            continue
        if any(kw in line_lower for kw in ['instruction', 'step', 'method', 'directions']):
            current_section = 'instructions'
            continue
        if any(kw in line_lower for kw in ['nutrition', 'calorie', 'macro']):
            current_section = 'nutrition'
            continue

        # Collect content based on section
        if current_section == 'ingredients' and line.strip():
            # Remove bullet points
            cleaned = line.strip().lstrip('-•*0123456789.) ')
            if cleaned:
                ingredients.append(cleaned)
        elif current_section == 'instructions' and line.strip():
            # Remove numbering
            cleaned = line.strip().lstrip('-•*0123456789.) ')
            if cleaned:
                instructions.append(cleaned)
        elif current_section == 'nutrition' and ':' in line:
            key, val = line.split(':', 1)
            key = key.strip().lower()
            val = val.strip()
            # Extract numeric values
            match = re.search(r'[\d.]+', val)
            if match:
                try:
                    nutrition[key] = float(match.group())
                except:
                    nutrition[key] = 0
            else:
                nutrition[key] = val

    if not name or not ingredients:
        return None

    # Extract nutrition values with defaults
    calories = int(nutrition.get('calories', 0))
    protein = int(nutrition.get('protein', 0))
    carbs = int(nutrition.get('carbs', 0) or nutrition.get('carbohydrates', 0))
    fat = int(nutrition.get('fat', 0))

    return {
        "name": name,
        "ingredients": ingredients,
        "instructions": instructions,
        "nutrition": {
            "calories": calories,
            "protein": protein,
            "carbs": carbs,
            "fat": fat,
        },
        "prep_time_minutes": 0,
        "cook_time_minutes": 0,
        "equipment": [],
    }


def parse_multiple_recipes(text: str) -> List[Dict[str, Any]]:
    """
    Parse multiple recipes from a text response.

    Args:
        text: Multi-recipe text, typically split by double newlines

    Returns:
        List of parsed recipe dicts
    """
    blocks = text.split('\n\n')
    recipes = []
    for block in blocks:
        recipe = parse_recipe_block(block)
        if recipe:
            recipes.append(recipe)
    return recipes


def extract_cooking_equipment(text: str) -> List[str]:
    """
    Extract cooking equipment mentions from recipe text.

    Args:
        text: Recipe text

    Returns:
        List of equipment names (lowercase)
    """
    equipment_keywords = {
        'air fryer': 'airfryer',
        'airfryer': 'airfryer',
        'thermomix': 'thermomix',
        'oven': 'oven',
        'stove': 'stove',
        'microwave': 'microwave',
        'slow cooker': 'slow_cooker',
        'instant pot': 'instant_pot',
        'blender': 'blender',
        'food processor': 'food_processor',
    }

    found = []
    text_lower = text.lower()
    for keyword, normalized in equipment_keywords.items():
        if keyword in text_lower:
            found.append(normalized)
    return list(set(found))


def estimate_prep_time(ingredients_count: int, instructions_count: int) -> int:
    """
    Rough estimate of prep time based on recipe complexity.

    Args:
        ingredients_count: Number of ingredients
        instructions_count: Number of steps

    Returns:
        Estimated prep time in minutes
    """
    base_time = 10
    ingredient_time = ingredients_count * 2
    instruction_time = instructions_count * 3
    return base_time + ingredient_time + instruction_time
