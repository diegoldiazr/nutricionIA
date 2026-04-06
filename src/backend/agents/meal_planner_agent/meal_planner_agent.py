"""
Meal Planner Agent - Generates meal suggestions based on remaining calories, macros, user preferences.
May call KnowledgeAgent when needed for nutrition facts.
"""
from typing import List, Dict, Any, Optional

class MealPlannerAgent:
    """
    Generates meal suggestions based on:
    - Remaining calories
    - Remaining macros (protein, carbs, fat)
    - User preferences (dietary restrictions, favorite foods, equipment)
    - Prep time constraints
    """
    
    def __init__(self, knowledge_agent, database, user_agent):
        """
        Initialize MealPlannerAgent.
        
        Args:
            knowledge_agent: KnowledgeAgent for nutrition queries
            database: Database service for meal history and preferences
            user_agent: UserAgent for user-specific data
        """
        self.knowledge_agent = knowledge_agent
        self.database = database
        self.user_agent = user_agent
    
    async def generate_meal_suggestions(
        self,
        user_id: int,
        remaining_calories: int,
        remaining_macros: Dict[str, int],
        meal_type: str = 'lunch',
        limit: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Generate meal suggestions for given constraints.
        
        Args:
            user_id: User ID
            remaining_calories: Calories remaining for the day
            remaining_macros: Dict with protein, carbs, fat remaining (in grams)
            meal_type: Type of meal (breakfast, lunch, dinner, snack)
            limit: Maximum number of suggestions to return
            
        Returns:
            List of meal suggestion dicts with name, ingredients, macros, prep_time, etc.
        """
        suggestions = []
        
        try:
            # Get user preferences
            preferences = await self.user_agent.get_preferences(user_id)
            
            # Query KnowledgeAgent for appropriate meals
            query = self._build_meal_query(
                meal_type, remaining_calories, remaining_macros, preferences
            )
            
            # Get nutritionally appropriate meal ideas from NotebookLM
            response = await self.knowledge_agent.query(query)
            
            # Parse response into structured meal suggestions
            parsed_meals = self._parse_knowledge_response(response)
            
            # Filter meals by constraints and get top N
            filtered_meals = self._filter_and_rank_meals(
                parsed_meals, remaining_calories, remaining_macros, preferences
            )
            
            suggestions = filtered_meals[:limit]
            
        except Exception as e:
            print(f"Error generating meal suggestions: {e}")
        
        return suggestions
    
    def _build_meal_query(
        self,
        meal_type: str,
        calories: int,
        macros: Dict[str, int],
        preferences: Dict[str, Any]
    ) -> str:
        """Build a natural language query for NotebookLM."""
        query_parts = [
            f"Suggest {meal_type} recipes with approximately {calories} calories",
            f"containing about {macros.get('protein', 0)}g protein, {macros.get('carbs', 0)}g carbs, {macros.get('fat', 0)}g fat"
        ]
        
        if preferences.get('dietary_restrictions'):
            query_parts.append(f"compatible with: {', '.join(preferences['dietary_restrictions'])}")
        
        if preferences.get('cooking_equipment'):
            query_parts.append(f"equipment: {', '.join(preferences['cooking_equipment'])}")
        
        if preferences.get('favorite_foods'):
            query_parts.append(f"include some of these ingredients: {', '.join(preferences['favorite_foods'][:5])}")
            
        if preferences.get('max_prep_time'):
            query_parts.append(f"prep time under {preferences['max_prep_time']} minutes")
            
        query_parts.append("Provide detailed ingredient lists, step-by-step instructions, and precise nutrition information for each recipe.")
        
        return " ".join(query_parts)
    
    def _parse_knowledge_response(self, response: str) -> List[Dict[str, Any]]:
        """
        Parse NotebookLM response into structured meal data.
        
        Expected format from NotebookLM:
        - Recipe name
        - Ingredients list with quantities
        - Instructions
        - Nutrition info (calories, protein, carbs, fat)
        - Prep/cook time
        """
        meals = []
        # Split response into individual recipes (assuming numbered or double newline separation)
        raw_recipes = response.split('\n\n')
        
        for raw in raw_recipes:
            meal = self._extract_recipe_data(raw)
            if meal:
                meals.append(meal)
        
        return meals
    
    def _extract_recipe_data(self, text: str) -> Optional[Dict[str, Any]]:
        """Extract structured recipe data from text block."""
        lines = text.strip().split('\n')
        if not lines:
            return None
            
        recipe = {
            'name': lines[0].strip(),
            'ingredients': [],
            'instructions': [],
            'nutrition': {},
            'prep_time_minutes': 0,
            'cook_time_minutes': 0
        }
        
        current_section = None
        for line in lines[1:]:
            line_lower = line.lower()
            
            if 'ingredient' in line_lower:
                current_section = 'ingredients'
                continue
            elif 'instruction' in line_lower or 'step' in line_lower:
                current_section = 'instructions'
                continue
            elif 'nutrition' in line_lower or 'calorie' in line_lower:
                current_section = 'nutrition'
                continue
            elif 'prep' in line_lower or 'cook' in line_lower:
                current_section = 'times'
                continue
                
            if current_section == 'ingredients' and line.strip():
                recipe['ingredients'].append(line.strip())
            elif current_section == 'instructions' and line.strip():
                recipe['instructions'].append(line.strip())
            elif current_section == 'nutrition' and ':' in line:
                key, value = line.split(':', 1)
                recipe['nutrition'][key.strip().lower()] = value.strip()
            elif current_section == 'times' and ':' in line:
                key, value = line.split(':', 1)
                key_lower = key.strip().lower()
                if 'prep' in key_lower:
                    recipe['prep_time_minutes'] = self._extract_minutes(value)
                elif 'cook' in key_lower:
                    recipe['cook_time_minutes'] = self._extract_minutes(value)
        
        # Ensure numeric fields
        if 'calories' in recipe['nutrition']:
            try:
                recipe['nutrition']['calories'] = int(recipe['nutrition']['calories'].split()[0])
            except:
                recipe['nutrition']['calories'] = 0
                
        return recipe if recipe['name'] and recipe['ingredients'] else None
    
    def _extract_minutes(self, time_str: str) -> int:
        """Extract minutes from time string like '25 minutes' or '1 hr 30 min'."""
        import re
        time_str = time_str.lower()
        if 'hour' in time_str or 'hr' in time_str:
            # Convert hours to minutes
            match = re.search(r'(\d+)\s*(?:hour|hr)', time_str)
            if match:
                hours = int(match.group(1))
                minutes_match = re.search(r'(\d+)\s*(?:min|minute)', time_str)
                minutes = int(minutes_match.group(1)) if minutes_match else 0
                return hours * 60 + minutes
        else:
            # Just minutes
            match = re.search(r'(\d+)', time_str)
            if match:
                return int(match.group(1))
        return 0
    
    def _filter_and_rank_meals(
        self,
        meals: List[Dict[str, Any]],
        remaining_calories: int,
        remaining_macros: Dict[str, int],
        preferences: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Filter meals that fit within macros and rank by preference match.
        """
        scored_meals = []
        
        for meal in meals:
            # Check calorie constraint (allow 10% overage)
            meal_cal = meal['nutrition'].get('calories', 0)
            if meal_cal > remaining_calories * 1.1:
                continue
            
            # Check macro constraints (allow 10% overage)
            meal_protein = meal['nutrition'].get('protein', 0)
            meal_carbs = meal['nutrition'].get('carbs', 0)
            meal_fat = meal['nutrition'].get('fat', 0)
            
            if (meal_protein > remaining_macros.get('protein', 0) * 1.1 or
                meal_carbs > remaining_macros.get('carbs', 0) * 1.1 or
                meal_fat > remaining_macros.get('fat', 0) * 1.1):
                continue
            
            # Calculate preference score
            score = self._calculate_preference_score(meal, preferences)
            scored_meals.append((score, meal))
        
        # Sort by score descending
        scored_meals.sort(key=lambda x: x[0], reverse=True)
        return [meal for score, meal in scored_meals]
    
    def _calculate_preference_score(self, meal: Dict[str, Any], preferences: Dict[str, Any]) -> float:
        """Calculate match score between meal and user preferences."""
        score = 0.0
        
        # Favorite ingredients boost
        meal_ingredients_str = ' '.join(meal['ingredients']).lower()
        for fav in preferences.get('favorite_foods', []):
            if fav.lower() in meal_ingredients_str:
                score += 10
        
        # Dietary restrictions penalty if violated
        for restriction in preferences.get('dietary_restrictions', []):
            if restriction.lower() in meal_ingredients_str:
                score -= 100  # Hard filter - should already be filtered out
                
        # Equipment requirement penalty if missing
        if preferences.get('cooking_equipment'):
            meal_text = ' '.join(meal['ingredients'] + meal['instructions']).lower()
            has_equipment = any(eq.lower() in meal_text for eq in preferences['cooking_equipment'])
            if not has_equipment:
                score -= 50
                
        # Prep time preference
        total_time = meal['prep_time_minutes'] + meal['cook_time_minutes']
        if preferences.get('max_prep_time') and total_time > preferences['max_prep_time']:
            score -= 20
            
        return score
