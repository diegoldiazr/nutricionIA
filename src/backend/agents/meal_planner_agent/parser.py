"""
Meal Parser - Parses recipe text into structured meal suggestions.

Handles various input formats from NotebookLM and other knowledge sources.
"""
import re
from typing import Dict, Any, List, Optional


def parse_multiple_recipes(text: str) -> List[Dict[str, Any]]:
    """
    Parse text containing one or more recipes into structured dicts.

    Args:
        text: Raw text from knowledge source

    Returns:
        List of meal suggestion dicts with nutrition info
    """
    if not text or not text.strip():
        return []

    # Try to split by recipe headers
    recipes = []
    parts = re.split(r'(?=\d+\.\s*[A-Z])|(?=Recipe\s+\d+)|(?=---\s*\n)', text, flags=re.IGNORECASE)

    for part in parts:
        part = part.strip()
        if len(part) < 50:
            continue
        recipe = parse_single_recipe(part)
        if recipe:
            recipes.append(recipe)

    return recipes


def parse_single_recipe(text: str) -> Optional[Dict[str, Any]]:
    """
    Parse a single recipe block into structured format.

    Expected format flexibility:
    - Name: Recipe Name
    - Ingredients: list
    - Instructions: steps
    - Nutrition: calories, protein, carbs, fat
    """
    lines = text.split('\n')
    recipe = {
        "name": "",
        "ingredients": [],
        "instructions": [],
        "nutrition": {},
        "prep_time_minutes": 0,
        "cook_time_minutes": 0,
        "equipment": [],
    }

    current_section = None
    section_content = []

    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'):
            continue

        # Detect section headers
        lower = line.lower()
        if re.match(r'^(name|recipe\s*title)[:\s]', lower):
            recipe["name"] = re.sub(r'^(name|recipe\s*title)[:\s]', '', line, flags=re.IGNORECASE).strip()
            current_section = None
            continue
        elif re.match(r'^(ingredients?|what\s+you\s+need)[:\s]', lower):
            current_section = 'ingredients'
            section_content = [re.sub(r'^[•\-\*\d\.]+\s*', '', line)]
            continue
        elif re.match(r'^(instructions?|directions?|steps?|how\s+to\s+make)[:\s]', lower):
            current_section = 'instructions'
            section_content = []
            continue
        elif re.match(r'^(nutrition|facts|macros?)[:\s]', lower):
            current_section = 'nutrition'
            section_content = [re.sub(r'^[•\-\*\d\.]+\s*', '', line)]
            continue
        elif re.match(r'^(time|prep|cook)[:\s]', lower):
            current_section = 'time'
            section_content = [line]
            continue
        elif re.match(r'^(equipment|tools)[:\s]', lower):
            current_section = 'equipment'
            section_content = [re.sub(r'^[•\-\*\d\.]+\s*', '', line)]
            continue

        # Collect content for current section
        if current_section == 'ingredients':
            cleaned = re.sub(r'^[•\-\*\d\.]+\s*', '', line)
            if cleaned:
                section_content.append(cleaned)
        elif current_section == 'instructions':
            cleaned = re.sub(r'^[•\-\*\d\.]+\s*', '', line)
            if cleaned:
                section_content.append(cleaned)
        elif current_section == 'nutrition':
            section_content.append(line)
        elif current_section == 'time':
            section_content.append(line)
        elif current_section == 'equipment':
            cleaned = re.sub(r'^[•\-\*\d\.]+\s*', '', line)
            if cleaned:
                section_content.append(cleaned)

    # Assign collected sections
    if section_content and current_section:
        if current_section == 'ingredients':
            recipe["ingredients"] = section_content
        elif current_section == 'instructions':
            recipe["instructions"] = section_content

    # Parse nutrition info
    recipe["nutrition"] = parse_nutrition(section_content if current_section == 'nutrition' else text)

    # Parse timing
    recipe["prep_time_minutes"] = parse_time(text, "prep")
    recipe["cook_time_minutes"] = parse_time(text, "cook")

    # Use first non-empty line as name if none found
    if not recipe["name"]:
        first_real_line = next((l.strip() for l in lines if l.strip() and not l.strip().startswith('#')), "")
        recipe["name"] = re.sub(r'^\d+\.\s*', '', first_real_line).strip()

    # Validate
    if not recipe["name"]:
        return None

    return recipe


def parse_nutrition(text: str) -> Dict[str, int]:
    """
    Extract nutrition values from text.

    Returns dict with calories, protein, carbs, fat (grams).
    """
    result = {"calories": 0, "protein": 0, "carbs": 0, "fat": 0}

    # Calories patterns
    cal_patterns = [
        r'calories?[:\s]*(\d+)',
        r'cal[:\s]*(\d+)',
        r'(\d+)\s*kcal',
        r'energy[:\s]*(\d+)',
    ]
    for pattern in cal_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            result["calories"] = int(match.group(1))
            break

    # Protein patterns
    prot_patterns = [
        r'protein[:\s]*(\d+)',
        r'prot[:\s]*(\d+)',
        r'(\d+)g?\s*protein',
    ]
    for pattern in prot_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            result["protein"] = int(match.group(1))
            break

    # Carbs patterns
    carb_patterns = [
        r'carbs?[:\s]*(\d+)',
        r'carbohydrates?[:\s]*(\d+)',
        r'(\d+)g?\s*carbs?',
    ]
    for pattern in carb_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            result["carbs"] = int(match.group(1))
            break

    # Fat patterns
    fat_patterns = [
        r'fat[:\s]*(\d+)',
        r'(\d+)g?\s*fat',
    ]
    for pattern in fat_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            result["fat"] = int(match.group(1))
            break

    return result


def parse_time(text: str, time_type: str = "prep") -> int:
    """
    Extract time in minutes from text.

    Args:
        text: Text to search
        time_type: "prep", "cook", or "total"
    """
    patterns = {
        "prep": [
            r'prep(?:aration)?\s*(?:time)?[:\s]*(\d+)\s*(?:min|minutes?)',
            r'(\d+)\s*min(?:utes?)?\s*prep',
        ],
        "cook": [
            r'cook(?:ing)?\s*(?:time)?[:\s]*(\d+)\s*(?:min|minutes?)',
            r'(\d+)\s*min(?:utes?)?\s*(?:of\s+)?cook(?:ing)?',
        ],
        "total": [
            r'total\s*(?:time)?[:\s]*(\d+)\s*(?:min|minutes?)',
            r'(\d+)\s*min(?:utes?)?\s*total',
        ]
    }

    for pattern in patterns.get(time_type, patterns["prep"]):
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return int(match.group(1))

    return 0
