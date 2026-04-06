"""
Knowledge Agent - Retrieves nutrition information from NotebookLM only.
Never fabricates facts. All responses must come from NotebookLM retrieval.
"""
import httpx
from typing import Optional

class KnowledgeAgent:
    """
    Responsible for retrieving nutrition information from NotebookLM.
    Prevents hallucinations by grounding all responses in NotebookLM data.
    """
    
    def __init__(self, connector):
        """
        Initialize KnowledgeAgent with a NotebookLM connector.
        
        Args:
            connector: NotebookLMConnector instance for API communication
        """
        self.connector = connector
    
    async def query(self, query: str, context: Optional[dict] = None) -> str:
        """
        Send a query to NotebookLM and return the grounded response.
        
        Args:
            query: The nutrition question to ask
            context: Optional context dict (user_id, dietary_restrictions, etc.)
            
        Returns:
            Response string from NotebookLM (never generates new info)
            
        Raises:
            Exception: If NotebookLM query fails
        """
        # Enrich query with context if provided
        enriched_query = self._enrich_query(query, context)
        
        # Send to NotebookLM
        response = await self.connector.send_query(enriched_query)
        
        # Validate response is not empty
        if not response or len(response.strip()) == 0:
            raise ValueError("Empty response from NotebookLM")
            
        return response
    
    def _enrich_query(self, query: str, context: Optional[dict]) -> str:
        """Add user context to query for better NotebookLM results."""
        if not context:
            return query
            
        context_parts = []
        if context.get('dietary_restrictions'):
            context_parts.append(f"Dietary restrictions: {', '.join(context['dietary_restrictions'])}")
        if context.get('goal'):
            context_parts.append(f"Goal: {context['goal']}")
            
        if context_parts:
            return f"{query}\nContext: {'; '.join(context_parts)}"
        return query
    
    async def validate_nutrition_fact(self, fact: str) -> bool:
        """
        Check if a nutrition claim is supported by NotebookLM.
        
        Args:
            fact: The nutrition claim to validate
            
        Returns:
            True if NotebookLM confirms the fact, False otherwise
        """
        validation_query = f"Is this nutrition fact accurate? {fact}"
        response = await self.connector.send_query(validation_query)
        
        # Simple heuristic: if NotebookLM confirms, it usually says "yes" or provides confirming info
        response_lower = response.lower()
        confirming_keywords = ['yes', 'correct', 'accurate', 'true', 'confirmed']
        denying_keywords = ['no', 'incorrect', 'false', 'not accurate', 'untrue']
        
        confirming_count = sum(1 for kw in confirming_keywords if kw in response_lower)
        denying_count = sum(1 for kw in denying_keywords if kw in response_lower)
        
        return confirming_count > denying_count
