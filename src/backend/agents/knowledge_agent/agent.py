"""
Knowledge Agent - Retrieves nutrition information from NotebookLM.

Prevents hallucinations by grounding all responses.
"""

from typing import Dict, Any
from ..base_agent import BaseAgent
from core.events import EventType
from core.exceptions import AgentError, ServiceError


class KnowledgeAgent(BaseAgent):
    """
    Queries NotebookLM for nutrition knowledge.
    """

    def __init__(
        self,
        agent_id: str = "knowledge",
        notebooklm_service=None,
        event_bus=None,
        **kwargs
    ):
        super().__init__(agent_id=agent_id, name="Knowledge Agent", event_bus=event_bus)
        self.notebooklm = notebooklm_service

    async def initialize(self) -> None:
        if not self.notebooklm:
            raise AgentError("NotebookLM service required")
        await super().initialize()

    async def process(self, request: Dict[str, Any]) -> Dict[str, Any]:
        query = request.get("query")
        if not query:
            raise AgentError("Query is required")
        if not self.notebooklm:
            return {"response": "", "error": "NotebookLM not configured"}
        try:
            response = await self.notebooklm.query(query, context=request.get("context", {}))
            return {
                "response": response.content if response else "",
                "sources": response.sources if response else [],
                "grounded": True
            }
        except Exception as e:
            raise ServiceError(f"NotebookLM query failed: {e}") from e
