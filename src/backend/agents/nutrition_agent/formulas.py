"""
Nutrition Formulas - Pure calculation functions for BMR, TDEE, and macronutrients.

All functions are stateless and testable without dependencies.
"""

from typing import Dict, Tuple


# Harris-Benedict constants ( Mifflin-St Jeor is more accurate, but this is what the code uses )
def calculate_bmr_male(weight_kg: float, height_cm: float, age: int) -> float:
    """BMR for males using Harris-Benedict."""
    return 66.47 + (13.75 * weight_kg) + (5.003 * height_cm) - (6.755 * age)


def calculate_bmr_female(weight_kg: float, height_cm: float, age: int) -> float:
    """BMR for females using Harris-Benedict."""
    return 655.1 + (9.563 * weight_kg) + (1.850 * height_cm) - (4.676 * age)


def calculate_bmr(weight_kg: float, height_cm: float, age: int, gender: str) -> float:
    """
    Calculate Basal Metabolic Rate (BMR).

    Args:
        weight_kg: Weight in kilograms
        height_cm: Height in centimeters
        age: Age in years
        gender: "male" or "female" (case-insensitive)

    Returns:
        BMR in calories per day
    """
    if gender.lower() in ('male', 'm'):
        return calculate_bmr_male(weight_kg, height_cm, age)
    else:
        return calculate_bmr_female(weight_kg, height_cm, age)


# Activity level multipliers (PAL - Physical Activity Level)
ACTIVITY_MULTIPLIERS = {
    'sedentary': 1.2,       # Little or no exercise
    'light': 1.375,         # Light exercise 1-3 days/week
    'moderate': 1.55,       # Moderate exercise 3-5 days/week
    'active': 1.725,        # Hard exercise 6-7 days/week
    'very_active': 1.9,     # Very hard exercise, physical job
}


def calculate_tdee(bmr: float, activity_level: str) -> float:
    """
    Calculate Total Daily Energy Expenditure (TDEE).

    Args:
        bmr: Basal metabolic rate
        activity_level: One of: sedentary, light, moderate, active, very_active

    Returns:
        TDEE in calories per day
    """
    multiplier = ACTIVITY_MULTIPLIERS.get(activity_level, 1.55)
    return bmr * multiplier


def calculate_macros(
    weight_kg: float,
    tdee: float,
    goal: str,
    activity_level: str = None
) -> Dict[str, int]:
    """
    Calculate daily macronutrient targets based on goal.

    Args:
        weight_kg: Current weight in kg
        tdee: Total daily energy expenditure
        goal: "lose_weight", "maintain", or "gain_muscle"
        activity_level: Optional, used to adjust protein intake

    Returns:
        Dict with calories, protein_grams, carbs_grams, fat_grams,
        plus percentage breakdowns.
    """
    # Adjust calories based on goal
    if goal == 'lose_weight':
        calories = tdee - 500  # 500 calorie deficit
    elif goal == 'gain_muscle':
        calories = tdee + 300  # 300 calorie surplus
    else:
        calories = tdee

    # Protein: higher for muscle preservation/gain
    if goal == 'lose_weight':
        protein_per_kg = 2.0
    elif goal == 'gain_muscle':
        protein_per_kg = 2.2
    else:
        protein_per_kg = 1.6

    protein_grams = weight_kg * protein_per_kg
    protein_calories = protein_grams * 4  # 4 cal/g

    # Fat: 25% of calories
    fat_grams = (calories * 0.25) / 9  # 9 cal/g
    fat_calories = fat_grams * 9

    # Carbs: remainder
    carbs_grams = max(0, (calories - protein_calories - fat_calories) / 4)  # 4 cal/g

    # Recalculate total to account for rounding
    total_cal = protein_calories + fat_calories + (carbs_grams * 4)

    return {
        'calories': int(round(calories)),
        'protein_grams': int(round(protein_grams)),
        'carbs_grams': int(round(carbs_grams)),
        'fat_grams': int(round(fat_grams)),
        'protein_percentage': round((protein_calories / total_cal) * 100, 1) if total_cal > 0 else 0,
        'fat_percentage': round((fat_calories / total_cal) * 100, 1) if total_cal > 0 else 0,
        'carbs_percentage': round(((carbs_grams * 4) / total_cal) * 100, 1) if total_cal > 0 else 0,
    }


def calculate_remaining_macros(
    target_macros: Dict[str, int],
    consumed_macros: Dict[str, int]
) -> Dict[str, int]:
    """
    Calculate remaining macros for the day.

    Args:
        target_macros: Target intake for the day
        consumed_macros: Already consumed amount

    Returns:
        Dict with remaining amounts (never negative)
    """
    return {
        'calories': max(0, target_macros['calories'] - consumed_macros.get('calories', 0)),
        'protein': max(0, target_macros['protein_grams'] - consumed_macros.get('protein', 0)),
        'carbs': max(0, target_macros['carbs_grams'] - consumed_macros.get('carbs', 0)),
        'fat': max(0, target_macros['fat_grams'] - consumed_macros.get('fat', 0)),
    }
