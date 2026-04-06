"""
Orchestrator Agent - Coordinates agent communication and flow.
Central controller that combines agent outputs.
"""
from typing import Dict, Any, Optional

class OrchestrationAgent:
    """
    Central controller that:
    - Coordinates agent communication
    - Combines results from multiple agents
    - Generates final output for frontend
    - Manages agent lifecycle
    """
    
    def __init__(self, agents: Dict[str, Any]):
        """
        Initialize orchestrator with all agents.
        
        Args:
            agents: Dict with keys: 'knowledge', 'nutrition', 'meal_planner', 'recommendation', 'progress', 'user', 'memory'
        """
        self.agents = agents
        self.knowledge_agent = agents.get('knowledge')
        self.nutrition_agent = agents.get('nutrition')
        self.meal_planner_agent = agents.get('meal_planner')
        self.recommendation_agent = agents.get('recommendation')
        self.progress_agent = agents.get('progress')
        self.user_agent = agents.get('user')
        self.memory_agent = agents.get('memory')
    
    async def process_daily_summary_request(self, user_id: int, date: str) -> Dict[str, Any]:
        """
        Generate daily summary by combining multiple agents.
        
        Flow:
        1. User data → Nutrition Agent → calculate actual vs target
        2. Meal suggestions ← Meal Planner Agent ← Knowledge Agent
        3. Combine all data → final summary
        """
        summary = {
            'user_id': user_id,
            'date': date,
            'nutrition_status': {},
            'meal_suggestions': [],
            'recommendations': {},
            'daily_macros': None
        }
        
        try:
            # 1. Get user profile
            user_profile = await self.user_agent.get_profile(user_id)
            
            # 2. Get daily logged macros
            daily_macros = await self.user_agent.get_daily_macros(user_id, date)
            summary['daily_macros'] = daily_macros
            
            # 3. Calculate targets
            targets = await self.nutrition_agent.calculate_targets(
                user_profile['weight_current'],
                user_profile['height'],
                user_profile['age'],
                user_profile['gender'],
                user_profile['activity_level'],
                user_profile['goal']
            )
            summary['nutrition_status']['targets'] = targets
            
            # 4. Compute remaining macros for meal planning
            if daily_macros:
                remaining = {
                    'calories': max(0, targets['calories'] - daily_macros['calories']),
                    'protein': max(0, targets['protein_grams'] - daily_macros['protein']),
                    'carbs': max(0, targets['carbs_grams'] - daily_macros['protein']),
                }
            else:
                remaining = {
                    'calories': targets['calories'],
                    'protein': targets['protein_grams'],
                    'carbs': targets['carbs_grams'],
                }
            summary['nutrition_status']['remaining'] = remaining
            
            # 5. Generate meal suggestions if needed
            if remaining['calories'] > 100:  # Still need to eat
                suggestions = await self.meal_planner_agent.generate_meal_suggestions(
                    user_id=user_id,
                    remaining_calories=remaining['calories'],
                    remaining_macros=remaining,
                    meal_type='dinner'  # Assume we're planning dinner
                )
                summary['meal_suggestions'] = suggestions
            
            # 6. Update memory patterns (if meal was logged)
            if daily_macros:
                await self.memory_agent.update_patterns(user_id, date, daily_macros)
            
        except Exception as e:
            print(f"Error in daily summary: {e}")
            summary['error'] = str(e)
        
        return summary
    
    async def process_progress_report_request(self, user_id: int, days: int = 7) -> Dict[str, Any]:
        """
        Generate weekly progress report.
        
        Flow:
        1. Get progress analysis from ProgressAgent
        2. Get recommendations from RecommendationAgent
        3. Combine into comprehensive report
        """
        report = {
            'user_id': user_id,
            'period_days': days,
            'progress_analysis': {},
            'recommendations': {},
            'summary': ''
        }
        
        try:
            # 1. Analyze progress
            progress = await self.progress_agent.analyze_progress(user_id, days)
            report['progress_analysis'] = progress
            
            # 2. Generate recommendations
            recommendations = await self.recommendation_agent.generate_recommendations(
                user_id, days
            )
            report['recommendations'] = recommendations
            
            # 3. Overall summary
            report['summary'] = self._generate_report_summary(progress, recommendations)
            
        except Exception as e:
            print(f"Error generating progress report: {e}")
            report['error'] = str(e)
        
        return report
    
    async def process_meal_logging(
        self,
        user_id: int,
        meal_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process a meal log entry.
        
        Flow:
        1. Validate meal data (maybe with KnowledgeAgent for nutrition info)
        2. Store via UserAgent
        3. Update daily macros
        4. Return current daily status
        """
        result = {
            'success': False,
            'meal_logged': None,
            'daily_status': None
        }
        
        try:
            # 1. Log meal
            logged_meal = await self.user_agent.log_meal(user_id, meal_data)
            result['meal_logged'] = logged_meal
            
            # 2. Get updated daily macros
            daily_status = await self.user_agent.get_daily_macros(
                user_id, meal_data['date']
            )
            result['daily_status'] = daily_status
            result['success'] = True
            
        except Exception as e:
            print(f"Error logging meal: {e}")
            result['error'] = str(e)
            
        return result
    
    async def process_recipe_suggestions(
        self,
        user_id: int,
        constraints: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Get recipe suggestions.
        
        Flow:
        1. Get user preferences
        2. Meal Planner → Knowledge Agent → recipes
        3. Filter by constraints
        """
        suggestions = []
        
        try:
            # Get user
            preferences = await self.user_agent.get_preferences(user_id)
            
            # Generate suggestions
            suggestions = await self.meal_planner_agent.generate_meal_suggestions(
                user_id=user_id,
                remaining_calories=constraints.get('calories', 0),
                remaining_macros=constraints.get('macros', {}),
                meal_type=constraints.get('meal_type', 'lunch'),
                limit=constraints.get('limit', 3)
            )
            
        except Exception as e:
            print(f"Error getting recipe suggestions: {e}")
            
        return {
            'suggestions': suggestions,
            'count': len(suggestions)
        }
    
    def _generate_report_summary(
        self,
        progress: Dict[str, Any],
        recommendations: Dict[str, Any]
    ) -> str:
        """
        Generate human-readable summary of progress report.
        """
        weight_change = progress.get('weight_change_weekly', 0)
        adherence = progress.get('adherence_rate', 0)
        
        summary_parts = []
        
        if abs(weight_change) > 0:
            summary_parts.append(f"Weight change this week: {weight_change/1000:.1f} kg")
        
        summary_parts.append(f"Meal logging adherence: {adherence*100:.0f}%")
        
        if recommendations.get('calorie_adjustment'):
            adj = recommendations['calorie_adjustment']
            summary_parts.append(f"Calorie recommendation: {adj['reason']}")
            
        return "\n".join(summary_parts)
    
    async def health_check(self) -> Dict[str, str]:
        """Check health of all agents."""
        health = {}
        for name, agent in self.agents.items():
            try:
                # Basic health check - agent responds
                if hasattr(agent, 'health'):
                    health[name] = await agent.health()
                else:
                    health[name] = 'operational'
            except Exception as e:
                health[name] = f'error: {str(e)}'
        return health
