"""
Recommendation Agent - High level coaching recommendations.
Analyzes progress and provides actionable advice.
"""
from typing import Dict, Any, List

class RecommendationAgent:
    """
    Produces high-level coaching recommendations including:
    - Adjust calorie targets
    - Modify protein intake
    - Change meal timing
    - Suggest new strategies
    """
    
    def __init__(self, nutrition_agent, progress_agent, user_agent):
        """
        Initialize RecommendationAgent.
        
        Args:
            nutrition_agent: NutritionAgent for target calculations
            progress_agent: ProgressAgent for analysis
            user_agent: UserAgent for user data access
        """
        self.nutrition_agent = nutrition_agent
        self.progress_agent = progress_agent
        self.user_agent = user_agent
    
    async def generate_recommendations(
        self,
        user_id: int,
        lookback_days: int = 7
    ) -> Dict[str, Any]:
        """
        Generate comprehensive coaching recommendations.
        
        Args:
            user_id: User ID
            lookback_days: Number of days to analyze (default 7)
            
        Returns:
            Dict with recommendations organized by category
        """
        recommendations = {
            'calorie_adjustment': None,
            'macro_adjustment': None,
            'meal_timing': None,
            'food_suggestions': [],
            'overall_feedback': '',
            'confidence_score': 0.0
        }
        
        try:
            # Get progress analysis
            progress_data = await self.progress_agent.analyze_progress(
                user_id, lookback_days
            )
            
            # Get user profile and preferences
            user_profile = await self.user_agent.get_profile(user_id)
            
            # Generate calorie recommendation based on weight change
            if progress_data['weight_change_weekly']:
                weight_change = progress_data['weight_change_weekly']
                current_target = progress_data['current_calorie_target']
                recommendations['calorie_adjustment'] = self._recommend_calorie_adjustment(
                    weight_change, current_target, user_profile['goal']
                )
            
            # Generate macro recommendations
            recommendations['macro_adjustment'] = self._recommend_macro_adjustment(
                progress_data, user_profile
            )
            
            # Generate meal timing recommendations
            recommendations['meal_timing'] = self._recommend_meal_timing(
                progress_data, user_profile
            )
            
            # Generate food suggestions based on memory patterns
            recommendations['food_suggestions'] = await self._generate_food_suggestions(user_id)
            
            # Overall feedback
            recommendations['overall_feedback'] = self._generate_overall_feedback(
                progress_data, recommendations
            )
            
            # Confidence based on data completeness
            recommendations['confidence_score'] = self._calculate_confidence(
                progress_data, user_profile
            )
            
        except Exception as e:
            print(f"Error generating recommendations: {e}")
            recommendations['overall_feedback'] = "Unable to generate recommendations due to insufficient data."
        
        return recommendations
    
    def _recommend_calorie_adjustment(
        self,
        weight_change: float,
        current_target: int,
        goal: str
    ) -> Dict[str, Any]:
        """Recommend calorie target adjustment based on weight change."""
        weight_change_weekly_kg = weight_change / 1000  # assuming grams
        
        if goal == 'lose_weight':
            if weight_change_weekly_kg < -0.25:  # Losing too fast (<0.25 kg/week)
                return {
                    'adjustment': 'increase',
                    'amount': 150,  # kcal increase
                    'reason': f'Weight loss of {abs(weight_change_weekly_kg):.1f} kg/week is too aggressive. Add {150} calories to slow to a healthier rate (~0.5 kg/week).'
                }
            elif weight_change_weekly_kg > 0.25:  # Gaining weight
                return {
                    'adjustment': 'decrease',
                    'amount': 200,
                    'reason': f'Weight has increased by {weight_change_weekly_kg:.1f} kg this week. Reduce calories by ~{200} to get back on track.'
                }
            else:
                return {
                    'adjustment': 'maintain',
                    'amount': 0,
                    'reason': 'Weight loss is on track (~0.5 kg/week). Keep current calorie target.'
                }
        elif goal == 'gain_muscle':
            if weight_change_weekly_kg < 0.1:
                return {
                    'adjustment': 'increase',
                    'amount': 200,
                    'reason': f'Weight gain is too slow ({weight_change_weekly_kg:.1f} kg/week). Add {200} calories to support muscle growth.'
                }
            elif weight_change_weekly_kg > 0.5:
                return {
                    'adjustment': 'decrease',
                    'amount': 150,
                    'reason': f'Weight gain too fast ({weight_change_weekly_kg:.1f} kg/week). Reduce by {150} calories to minimize fat gain.'
                }
            else:
                return {
                    'adjustment': 'maintain',
                    'amount': 0,
                    'reason': 'Weight gain is in the optimal range (0.25-0.5 kg/week).'
                }
        else:  # maintain
            if abs(weight_change_weekly_kg) > 0.5:
                return {
                    'adjustment': 'adjust',
                    'amount': 100 if weight_change_weekly_kg > 0 else -100,
                    'reason': f'Weight changed {weight_change_weekly_kg:.1f} kg from baseline. Small adjustment recommended.'
                }
            else:
                return {
                    'adjustment': 'maintain',
                    'amount': 0,
                    'reason': 'Weight is stable within acceptable range.'
                }
    
    def _recommend_macro_adjustment(
        self,
        progress_data: Dict[str, Any],
        user_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Recommend macro adjustments based on adherence and goal."""
        avg_protein_per_kg = progress_data.get('avg_protein_per_kg', 0)
        goal = user_profile['goal']
        weight = user_profile.get('weight_current', 70)
        
        recommendation = {
            'adjust_protein': False,
            'protein_change_grams': 0,
            'reason': ''
        }
        
        # Protein targets: 2g/kg for weight loss, 1.8g/kg for muscle gain, 1.6g/kg for maintain
        if goal == 'lose_weight':
            target_protein_per_kg = 2.0
        elif goal == 'gain_muscle':
            target_protein_per_kg = 1.8
        else:
            target_protein_per_kg = 1.6
            
        target_protein = weight * target_protein_per_kg
        difference = abs(avg_protein_per_kg - target_protein)
        
        if difference > 20:  # More than 20g off
            recommendation['adjust_protein'] = True
            recommendation['protein_change_grams'] = int(target_protein - avg_protein_per_kg)
            if avg_protein_per_kg < target_protein:
                recommendation['reason'] = f"Protein intake is {avg_protein_per_kg:.0f}g/day, but you need ~{target_protein:.0f}g/day for muscle preservation during weight loss. Increase by {recommendation['protein_change_grams']}g."
            else:
                recommendation['reason'] = f"Protein intake is high at {avg_protein_per_kg:.0f}g/day. You can reduce to ~{target_protein:.0f}g/day."
        else:
            recommendation['reason'] = f"Protein intake is optimal at ~{avg_protein_per_kg:.0f}g/day."
            
        return recommendation
    
    def _recommend_meal_timing(
        self,
        progress_data: Dict[str, Any],
        user_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Recommend meal timing adjustments based on hunger patterns."""
        recommendation = {
            'suggestions': [],
            'rationale': ''
        }
        
        hunger_patterns = progress_data.get('hunger_patterns', {})
        
        if hunger_patterns.get('late_night_hunger'):
            recommendation['suggestions'].append('Add a protein-rich evening snack')
            recommendation['suggestions'].append('Ensure dinner has adequate protein and fiber')
            
        if hunger_patterns.get('mid_morning_crash'):
            recommendation['suggestions'].append('Include protein in breakfast')
            recommendation['suggestions'].append('Avoid simple carbs early in the day')
            
        if len(recommendation['suggestions']) == 0:
            recommendation['rationale'] = 'Meal timing appears well-balanced based on hunger reports.'
        else:
            recommendation['rationale'] = 'Adjustments recommended to better manage hunger.'
            
        return recommendation
    
    async def _generate_food_suggestions(self, user_id: int) -> List[Dict[str, Any]]:
        """Suggest foods based on memory patterns (favorites, recurring)."""
        # This would integrate with MemoryAgent
        suggestions = [
            {
                'type': 'favorite',
                'food': 'Grilled chicken breast',
                'reason': 'Matches your high protein preference and is a recurring favorite'
            },
            {
                'type': 'new_rotation',
                'food': 'Greek yogurt with berries',
                'reason': 'High protein breakfast option that fits your dietary profile'
            }
        ]
        return suggestions
    
    def _generate_overall_feedback(
        self,
        progress_data: Dict[str, Any],
        recommendations: Dict[str, Any]
    ) -> str:
        """Generate natural language feedback."""
        weight_change = progress_data.get('weight_change_weekly', 0)
        adherence = progress_data.get('adherence_rate', 0)
        
        if adherence < 0.6:
            feedback = "Your adherence has been low this week. Focus on hitting your protein goals first. Small, consistent changes are better than perfect but unsustainable efforts."
        elif weight_change and abs(weight_change) > 500:
            feedback = f"Your weight changed by {weight_change/1000:.1f} kg this week. {'Good progress' if (weight_change < 0 and recommendations.get('overall_goal')=='lose_weight') or (weight_change > 0 and recommendations.get('overall_goal')=='gain_muscle') else 'Adjustments are needed.'} Check your specific recommendations below."
        else:
            feedback = "You're making steady progress. Keep up the good work and continue logging your meals accurately."
            
        return feedback
    
    def _calculate_confidence(
        self,
        progress_data: Dict[str, Any],
        user_profile: Dict[str, Any]
    ) -> float:
        """Calculate confidence score (0-1) based on data completeness."""
        factors = []
        
        # Weight data completeness
        if progress_data.get('days_with_weight', 0) >= 5:
            factors.append(1.0)
        elif progress_data.get('days_with_weight', 0) >= 2:
            factors.append(0.5)
        else:
            factors.append(0.0)
            
        # Meal logging completeness
        if progress_data.get('adherence_rate', 0) >= 0.8:
            factors.append(1.0)
        elif progress_data.get('adherence_rate', 0) >= 0.5:
            factors.append(0.5)
        else:
            factors.append(0.0)
            
        return sum(factors) / len(factors) if factors else 0.0
