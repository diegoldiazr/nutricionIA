"""
NotebookLM Service - Provides access to NotebookLM knowledge base.
"""
import httpx
from typing import Dict, Any, Optional
from pydantic import BaseModel
from datetime import datetime
from tenacity import retry, stop_after_attempt, wait_exponential
import logging

logger = logging.getLogger(__name__)

class NotebookLMResponse(BaseModel):
    """Standardized response from NotebookLM."""
    content: str
    sources: list = []
    confidence: float = 0.0
    timestamp: datetime = None

class NotebookLMService:
    """Queries NotebookLM API with proper authentication and retry logic."""
    
    def __init__(self, api_url: str, notion_token: str, timeout: float = 30.0, max_retries: int = 3):
        self.api_url = api_url
        self.notion_token = notion_token
        self.timeout = timeout
        self.max_retries = max_retries
        self._session: Optional[httpx.AsyncClient] = None
    
    async def ensure_session(self) -> httpx.AsyncClient:
        if self._session is None:
            self._session = httpx.AsyncClient(timeout=httpx.Timeout(self.timeout))
        return self._session
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def query(self, question: str, context: Dict[str, Any] = None) -> Optional[NotebookLMResponse]:
        try:
            session = await self.ensure_session()
            headers = {
                "Authorization": f"Bearer {self.notion_token}",
                "Content-Type": "application/json",
            }
            payload = {"query": question, "context": context or {}, "include_sources": True}
            response = await session.post(f"{self.api_url}/query", json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            return NotebookLMResponse(
                content=data.get("answer", ""),
                sources=data.get("sources", []),
                confidence=data.get("confidence", 0.0),
                timestamp=datetime.utcnow()
            )
        except httpx.HTTPError as e:
            logger.error(f"NotebookLM query failed: {e}")
            return None
        except Exception as e:
            logger.exception(f"Unexpected error querying NotebookLM: {e}")
            return None
    
    async def health(self) -> Dict[str, Any]:
        try:
            result = await self.query("test", {})
            return {"status": "healthy" if result else "unhealthy", "api_url": self.api_url}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}
    
    async def close(self) -> None:
        if self._session:
            await self._session.aclose()
            self._session = None
    
    def __del__(self):
        import asyncio
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                loop.create_task(self.close())
            else:
                loop.run_until_complete(self.close())
        except:
            pass
