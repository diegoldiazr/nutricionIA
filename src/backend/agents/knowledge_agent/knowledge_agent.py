"""
Knowledge Agent - Retrieves nutrition information from NotebookLM only.
Never fabricates facts. All responses must come from NotebookLM retrieval.
"""
from typing import Dict, Any, Optional, List
from .base_agent import BaseAgent
from ...services.notebooklm_connector import NotebookLMConnector


class KnowledgeAgent(BaseAgent):
    """
    Responsible for retrieving nutrition information from NotebookLM.
    Prevents hallucinations by grounding all responses in NotebookLM data.
    """

    def __init__(self, agent_id: str = "knowledge", connector: NotebookLMConnector = None):
        super().__init__(agent_id=agent_id, name="Knowledge Agent")
        self.connector = connector
        self.cache: Dict[str, str] = {}

    async def initialize(self) -> None:
        await super().initialize()
        if self.connector:
            pass

    async def process(self, request: Dict[str, Any]) -> Dict[str, Any]:
        query = request.get("query")
        if not query:
            raise ValueError("Query is required")

        context = request.get("context", {})
        use_cache = request.get("cache", True)
        user_id = request.get("user_id")

        enriched_query = self._enrich_query(query, context)

        if use_cache and enriched_query in self.cache:
            return {
                "response": self.cache[enriched_query],
                "source": "notebooklm",
                "cached": True,
                "confidence": 0.95
            }

        try:
            response = await self.connector.send_query(enriched_query)
            if use_cache:
                self.cache[enriched_query] = response
            return {
                "response": response,
                "source": "notebooklm",
                "cached": False,
                "confidence": 0.9
            }
        except Exception as e:
            return {
                "response": f"Knowledge retrieval failed: {str(e)}",
                "source": "error",
                "cached": False,
                "confidence": 0.0
            }

    def _enrich_query(self, query: str, context: Dict[str, Any]) -> str:
        if not context:
            return query
        context_parts = []
        if context.get('dietary_restrictions'):
            context_parts.append(f"Dietary restrictions: {', '.join(context['dietary_restrictions'])}")
        if context.get('goal'):
            context_parts.append(f"Goal: {context['goal']}")
        if context.get('allergies'):
            context_parts.append(f"Allergies: {', '.join(context['allergies'])}")
        if context_parts:
            return f"{query}\nUser context: {'; '.join(context_parts)}"
        return query

    async def validate_fact(self, fact: str) -> Dict[str, Any]:
        validation_query = f"Is this nutrition fact accurate? {fact}"
        response = await self.connector.send_query(validation_query)
        response_lower = response.lower()
        confirming = ['yes', 'correct', 'accurate', 'true', 'confirmed', 'right']
        denying = ['no', 'incorrect', 'false', 'not accurate', 'untrue', 'wrong']
        confirming_count = sum(1 for kw in confirming if kw in response_lower)
        denying_count = sum(1 for kw in denying if kw in response_lower)
        is_valid = confirming_count > denying_count
        confidence = 0.8 if is_valid else 0.2
        return {
            "valid": is_valid,
            "explanation": response[:200],
            "confidence": confidence
        }

    def clear_cache(self) -> None:
        self.cache.clear()
