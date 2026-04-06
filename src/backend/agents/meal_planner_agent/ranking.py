"""
Meal Ranking - Pure functions for ranking and scoring meal suggestions.

All functions are stateless and testable.
"""

from typing import List, Dict, Any


def rank_suggestions(
    meals: List[Dict[str, Any]],
    target_macros: Dict[str, int],
    preferences: Dict[str, Any],
    weights: Dict[str, float] = None
) -> List[Dict[str, Any]]:
    """
    Rank meal suggestions based on multiple criteria.

    Args:
        meals: List of meal suggestion dicts
        target_macros: Target macros (calories, protein, carbs, fat)
        preferences: User preferences dict
        weights: Scoring weights for each criterion (defaults provided)

    Returns:
        Meals sorted by score (highest first)
    """
    if weights is None:
        weights = {
            'macro_match': 0.4,
            'preference_match': 0.3,
            'variety': 0.2,
            'simplicity': 0.1,
        }

    scored_meals = []
    for meal in meals:
        score = calculate_meal_score(meal, target_macros, preferences, weights)
        scored_meals.append((score, meal))

    scored_meals.sort(key=lambda x: x[0], reverse=True)
    return [meal for score, meal in scored_meals]


def calculate_meal_score(
    meal: Dict[str, Any],
    target_macros: Dict[str, int],
    preferences: Dict[str, Any],
    weights: Dict[str, float]
) -> float:
    """
    Calculate composite score for a meal suggestion.

    Args:
        meal: Meal suggestion dict with nutrition info
        target_macros: Target macros to aim for
        preferences: User preferences
        weights: Criterion weights

    Returns:
        Composite score (higher is better)
    """
    total_score = 0.0

    # Macro closeness score (0-100)
    macro_score = score_macro_match(meal, target_macros)
    total_score += macro_score * weights.get('macro_match', 0.4)

    # Preference match score (0-100)
    pref_score = score_preference_match(meal, preferences)
    total_score += pref_score * weights.get('preference_match', 0.3)

    # Variety score (encourage variety) - simple implementation
    variety_score = 50  # TODO: implement based on meal history
    total_score += variety_score * weights.get('variety', 0.2)

    # Simplicity score (shorter prep/cook time is better)
    simplicity_score = score_simplicity(meal)
    total_score += simplicity_score * weights.get('simplicity', 0.1)

    return total_score


def score_macro_match(meal: Dict[str, Any], target_macros: Dict[str, int]) -> float:
    """
    Score how close meal macros are to target.

    Args:
        meal: Meal with nutrition dict
        target_macros: Target values

    Returns:
        0-100 score (higher = closer match)
    """
    nut = meal.get('nutrition', {})
    if not nut:
        return 0

    # Calorie deviation penalty
    cal_target = target_macros.get('calories', 500)
    cal_actual = nut.get('calories', 0)
    cal_diff = abs(cal_actual - cal_target)
    cal_score = max(0, 100 - (cal_diff / cal_target * 100))

    # Protein deviation penalty
    protein_target = target_macros.get('protein', 30)
    protein_actual = nut.get('protein', 0)
    protein_diff = abs(protein_actual - protein_target)
    protein_score = max(0, 100 - (protein_diff / max(1, protein_target) * 100))

    # Weighted macro score (calories 50%, protein 30%, carbs/fat 20%)
    return cal_score * 0.5 + protein_score * 0.3 + 25  # carbs/fat placeholder


def score_preference_match(meal: Dict[str, Any], preferences: Dict[str, Any]) -> float:
    """
    Score how well meal matches user preferences.

    Args:
        meal: Meal dict
        preferences: User preferences dict

    Returns:
        0-100 score
    """
    score = 50  # Base score

    # Favorite foods bonus
    favorite_foods = preferences.get('favorite_foods', [])
    if favorite_foods:
        meal_text = ' '.join(meal.get('ingredients', []) + [meal.get('name', '')]).lower()
        matches = sum(1 for food in favorite_foods if food.lower() in meal_text)
        score += min(matches * 15, 30)  # Cap at +30

    # Dietary restrictions check (penalty if violated)
    dietary_restrictions = preferences.get('dietary_restrictions', [])
    # TODO: implement restriction checking logic
    if dietary_restrictions:
        score -= 10  # Placeholder penalty for potential violation

    # Equipment match bonus
    equipment_prefs = preferences.get('cooking_equipment', [])
    meal_equipment = meal.get('equipment', [])
    if equipment_prefs and meal_equipment:
        overlap = set(equipment_prefs) & set(meal_equipment)
        if overlap:
            score += 20

    # Prep time penalty
    prep_time_max = preferences.get('prep_time_max', 45)
    meal_prep = meal.get('prep_time_minutes', 0)
    if meal_prep > prep_time_max:
        score -= 20

    return max(0, min(100, score))


def score_simplicity(meal: Dict[str, Any]) -> float:
    """
    Score based on simplicity (fewer ingredients, fewer steps).

    Args:
        meal: Meal dict

    Returns:
        0-100 score (100 = very simple)
    """
    ingredients_count = len(meal.get('ingredients', []))
    instructions_count = len(meal.get('instructions', []))

    # Fewer ingredients = simpler
    if ingredients_count <= 3:
        ing_score = 100
    elif ingredients_count <= 6:
        ing_score = 80
    elif ingredients_count <= 10:
        ing_score = 60
    else:
        ing_score = 30

    # Fewer steps = simpler
    if instructions_count <= 3:
        step_score = 100
    elif instructions_count <= 6:
        step_score = 80
    elif instructions_count <= 10:
        step_score = 60
    else:
        step_score = 30

    return (ing_score + step_score) / 2


def diversify_suggestions(
    meals: List[Dict[str, Any]],
    min_variety_distance: float = 0.3
) -> List[Dict[str, Any]]:
    """
    Ensure variety in suggestions by removing too-similar meals.
    Simple implementation based on ingredient overlap.

    Args:
        meals: Ranked list of meals
        min_variety_distance: Minimum similarity threshold (0-1)

    Returns:
        Filtered list with diverse options
    """
    if len(meals) <= 1:
        return meals

    selected = [meals[0]]

    for candidate in meals[1:]:
        # Check similarity to each selected meal
        too_similar = False
        for selected_meal in selected:
            similarity = calculate_ingredient_similarity(
                candidate.get('ingredients', []),
                selected_meal.get('ingredients', [])
            )
            if similarity > min_variety_distance:
                too_similar = True
                break

        if not too_similar:
            selected.append(candidate)

    return selected


def calculate_ingredient_similarity(ingredients1: List[str], ingredients2: List[str]) -> float:
    """
    Calculate Jaccard similarity between two ingredient sets.

    Args:
        ingredients1: First ingredient list
        ingredients2: Second ingredient list

    Returns:
        0-1 similarity score
    """
    set1 = set(i.lower().strip() for i in ingredients1)
    set2 = set(i.lower().strip() for i in ingredients2)

    if not set1 or not set2:
        return 0.0

    intersection = set1 & set2
    union = set1 | set2

    return len(intersection) / len(union)
