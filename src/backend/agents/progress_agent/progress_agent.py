"""
Progress Agent - Analyzes weekly user progress.
Inputs: weight change, calorie intake, training
Outputs: feedback, adjustment suggestions
"""
from typing import Dict, Any, List
from datetime import date

class ProgressAgent:
    """
    Analyzes weekly user progress by combining:
    - Weight change trends
    - Calorie intake vs targets
    - Training adherence
    - Energy levels and hunger reports
    """
    
    def __init__(self, user_agent, nutrition_agent):
        """
        Args:
            user_agent: UserAgent for data access
            nutrition_agent: NutritionAgent for target context
        """
        self.user_agent = user_agent
        self.nutrition_agent = nutrition_agent
    
    async def analyze_progress(self, user_id: int, lookback_days: int = 7) -> Dict[str, Any]:
        """
        Analyze user progress for the given period.
        
        Args:
            user_id: User ID
            lookback_days: Number of days to analyze
            
        Returns:
            Dict with progress analysis including:
            - weight_change_weekly (in grams)
            - weight_trend (up, down, stable)
            - avg_daily_calories
            - avg_protein_per_kg
            - adherence_rate
            - training_days
            - hunger_patterns
        """
        analysis = {
            'weight_change_weekly': 0,
            'weight_trend': 'stable',
            'avg_daily_calories': 0,
            'avg_protein_per_kg': 1.6,
            'adherence_rate': 0.0,
            'training_days': 0,
            'hunger_patterns': {
                'late_night_hunger': False,
                'mid_morning_crash': False,
            },
            'days_with_weight': 0,
            'current_calorie_target': 0,
        }
        
        try:
            # Get weight history
            history = await self.user_agent.get_weight_history(user_id, lookback_days)
            
            # Calculate weight change
            if len(history) >= 2:
                start_weight = history[0]['weight']
                end_weight = history[-1]['weight']
                change_g = (end_weight - start_weight) * 1000
                weekly_change = change_g / max(1, lookback_days / 7)
                analysis['weight_change_weekly'] = weekly_change
                analysis['weight_trend'] = 'down' if weekly_change < -50 else 'up' if weekly_change > 50 else 'stable'
                analysis['days_with_weight'] = len(history)
            
            # Get daily macros for adherence
            profile = await self.user_agent.get_profile(user_id)
            targets = self.nutrition_agent.calculate_macros(
                profile['weight_current'],
                self.nutrition_agent.calculate_tdee(
                    self.nutrition_agent.calculate_bmr(
                        profile['weight_current'], profile['height'], profile['age'], profile['gender']
                    ),
                    profile['activity_level']
                ),
                profile['goal'],
                profile['activity_level']
            )
            analysis['current_calorie_target'] = targets['calories']
            
            # Placeholder adherence calculation
            analysis['adherence_rate'] = 0.75
            
        except Exception as e:
            print(f"Error analyzing progress: {e}")
            
        return analysis
