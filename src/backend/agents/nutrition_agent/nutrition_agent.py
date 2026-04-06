from typing import Dict, Any, Optional

class NutritionAgent:
    """
    Responsible for calculating physiological metrics and targets.
    Uses NotebookLM validation through KnowledgeAgent when needed.
    """
    
    def __init__(self, knowledge_agent, database):
        self.knowledge_agent = knowledge_agent
        self.database = database
    
    def calculate_bmr(self, weight: float, height: float, age: int, gender: str) -> float:
        if gender.lower() == 'male':
            bmr = 66.47 + (13.75 * weight) + (5.003 * height) - (6.755 * age)
        else:
            bmr = 655.1 + (9.563 * weight) + (1.850 * height) - (4.676 * age)
        return bmr
    
    def calculate_tdee(self, bmr: float, activity_level: str) -> float:
        multipliers = {
            'sedentary': 1.2,
            'light': 1.375,
            'moderate': 1.55,
            'active': 1.725,
            'very_active': 1.9,
        }
        multiplier = multipliers.get(activity_level, 1.55)
        return bmr * multiplier
    
    def calculate_macros(self, weight: float, tdee: float, goal: str, activity_level: str) -> Dict[str, int]:
        if goal == 'lose_weight':
            calories = tdee - 500
        elif goal == 'gain_muscle':
            calories = tdee + 300
        else:
            calories = tdee

        protein_per_kg = 2.0 if goal == 'lose_weight' else 1.8 if goal == 'gain_muscle' else 1.6
        protein_grams = weight * protein_per_kg

        fat_calories = calories * 0.25
        fat_grams = fat_calories / 9

        protein_calories = protein_grams * 4
        fat_calories_actual = fat_grams * 9
        carbs_calories = calories - protein_calories - fat_calories_actual
        carbs_grams = max(0, carbs_calories / 4)

        protein_pct = (protein_grams * 4 / calories) * 100
        fat_pct = (fat_grams * 9 / calories) * 100
        carbs_pct = (carbs_grams * 4 / calories) * 100

        return {
            'calories': int(calories),
            'protein_grams': int(protein_grams),
            'carbs_grams': int(carbs_grams),
            'fat_grams': int(fat_grams),
            'protein_percentage': round(protein_pct, 1),
            'fat_percentage': round(fat_pct, 1),
            'carbs_percentage': round(carbs_pct, 1),
        }

    async def validate_macros(self, macros: Dict[str, Any], user_context: Dict[str, Any]) -> Dict[str, bool]:
        result = {
            'protein': True,
            'carbs': True,
            'fat': True,
            'overall': True,
            'warnings': []
        }
        if not self.knowledge_agent:
            return result
        try:
            query = (
                f"Are these macros appropriate for a {user_context.get('gender', 'unknown')} "
                f"with {user_context.get('weight_current', 0)} kg, goal {user_context.get('goal', 'maintain')} "
                f"eating {macros.get('calories', 0)} cal, {macros.get('protein_grams', 0)}g protein, "
                f"{macros.get('carbs_grams', 0)}g carbs, {macros.get('fat_grams', 0)}g fat?"
            )
            response = await self.knowledge_agent.query(query)
            warning_keywords = ['too high', 'too low', 'insufficient', 'excessive', 'concern']
            for kw in warning_keywords:
                if kw in response.lower():
                    result['overall'] = False
                    result['warnings'].append(f"KnowledgeAgent flagged: {response[:100]}")
        except Exception as e:
            result['warnings'].append(f"Validation error: {str(e)}")
        return result
