"""
NotebookLM Connector - Communication layer with NotebookLM.

Responsibilities:
- Google OAuth authentication (via Notion token)
- Query NotebookLM knowledge base
- Return structured responses
- Handle rate limiting and retries

All nutrition knowledge must pass through this connector.
No nutrition facts should be generated without NotebookLM grounding.
"""
import os
import httpx
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
from datetime import datetime
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import logging

logger = logging.getLogger(__name__)


class NotebookLMConfig(BaseModel):
    """Configuration for NotebookLM connector."""
    notion_token: str = Field(..., description="Notion integration token")
    workspace_id: str = Field(..., description="NotebookLM workspace ID or URL")
    api_url: str = Field("https://notebooklm.googleapis.com/v1", description="NotebookLM API base URL")
    timeout: float = Field(30.0, description="Request timeout in seconds")
    max_retries: int = Field(3, description="Maximum retry attempts")


class NotebookLMQuery(BaseModel):
    """Structured query to NotebookLM."""
    prompt: str
    context: Optional[Dict[str, Any]] = None
    sources: Optional[List[str]] = None
    max_results: int = 5
    include_citations: bool = True


class NotebookLMResponse(BaseModel):
    """Structured response from NotebookLM."""
    answer: str
    sources: List[Dict[str, Any]] = []
    confidence: float = 0.0
    citations: List[Dict[str, Any]] = []
    metadata: Dict[str, Any] = {}
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    error: Optional[str] = None


class NotebookLMConnector:
    """
    Handles all communication with NotebookLM workspace.
    Retrieves knowledge only - never generates nutrition facts independently.
    """

    def __init__(
        self,
        config: NotebookLMConfig = None,
        token: str = None,
        workspace_id: str = None,
    ):
        """
        Initialize NotebookLM connector.

        Args:
            config: Configuration object (loads from env if None)
            token: Notion token (overrides env if provided)
            workspace_id: NotebookLM workspace ID or URL (overrides env if provided)
        """
        if config:
            self.config = config
        else:
            # Use provided values or fall back to environment
            notion_token = token or os.getenv("NOTION_TOKEN", "")
            workspace = workspace_id or os.getenv("NOTION_WORKSPACE", "")
            api_url = os.getenv("NOTEBOOKLM_API_URL", "https://notebooklm.googleapis.com/v1")

            self.config = NotebookLMConfig(
                notion_token=notion_token,
                workspace_id=workspace,
                api_url=api_url,
                timeout=float(os.getenv("NOTEBOOKLM_TIMEOUT", "30.0")),
                max_retries=int(os.getenv("NOTEBOOKLM_MAX_RETRIES", "3")),
            )

        if not self.config.notion_token:
            raise ValueError("NOTION_TOKEN environment variable or token parameter is required")

        if not self.config.workspace_id:
            logger.warning("NOTION_WORKSPACE not set - some operations may fail")

        self.base_url = self.config.api_url.rstrip('/')
        self._session: Optional[httpx.AsyncClient] = None

    async def ensure_session(self) -> httpx.AsyncClient:
        """Ensure HTTP client session is initialized."""
        if self._session is None:
            self._session = httpx.AsyncClient(
                headers=self._build_headers(),
                timeout=httpx.Timeout(self.config.timeout)
            )
        return self._session

    def _build_headers(self) -> Dict[str, str]:
        """Build authentication headers for NotebookLM API."""
        return {
            "Authorization": f"Bearer {self.config.notion_token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((httpx.HTTPError, httpx.TimeoutException)),
        before_sleep=lambda retry_state: logger.warning(f"Retrying NotebookLM request (attempt {retry_state.attempt_number})")
    )
    async def send_query(self, query: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Send a query to NotebookLM and return the answer text.

        Args:
            query: The question/prompt to send
            context: Optional context dict to enrich the query

        Returns:
            Response text from NotebookLM

        Raises:
            ValueError: If query fails or response is invalid
        """
        try:
            notebook_query = NotebookLMQuery(prompt=query, context=context)
            session = await self.ensure_session()

            # Determine endpoint
            endpoint = f"{self.base_url}/workspaces/{self.config.workspace_id}/query"
            if self.config.workspace_id.startswith("http"):
                endpoint = f"{self.base_url}/query"

            payload = notebook_query.model_dump(exclude_none=True)
            logger.debug(f"NotebookLM query: {query[:100]}...")
            response = await session.post(endpoint, json=payload)
            response.raise_for_status()

            lm_response = NotebookLMResponse(**response.json())
            if lm_response.error:
                raise ValueError(f"NotebookLM error: {lm_response.error}")

            logger.info(f"NotebookLM response received (confidence: {lm_response.confidence})")
            return lm_response.answer

        except httpx.HTTPStatusError as e:
            error_msg = f"NotebookLM API {e.response.status_code}"
            try:
                err = e.response.json()
                error_msg = f"NotebookLM error: {err.get('error', err.get('message', e.response.text[:100]))}"
            except: pass
            logger.error(error_msg)
            raise ValueError(error_msg) from e
        except Exception as e:
            logger.exception(f"NotebookLM query failed: {e}")
            raise

    async def query_with_sources(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None,
        source_ids: Optional[List[str]] = None
    ) -> NotebookLMResponse:
        """Query with specific source documents."""
        notebook_query = NotebookLMQuery(prompt=query, context=context, sources=source_ids, max_results=10)
        session = await self.ensure_session()
        endpoint = f"{self.base_url}/workspaces/{self.config.workspace_id}/query"
        if self.config.workspace_id.startswith("http"):
            endpoint = f"{self.base_url}/query"
        response = await session.post(endpoint, json=notebook_query.model_dump(exclude_none=True))
        response.raise_for_status()
        return NotebookLMResponse(**response.json())

    async def validate_nutrition_fact(self, fact: str) -> Dict[str, Any]:
        """Validate a nutrition fact against NotebookLM knowledge."""
        validation_query = f"Is this nutrition fact accurate? Fact: {fact}"
        try:
            response = await self.send_query(validation_query)
            rl = response.lower()
            confirming = ['yes', 'correct', 'accurate', 'true', 'confirmed', 'valid']
            denying = ['no', 'incorrect', 'false', 'not accurate', 'untrue', 'invalid']
            confirming_count = sum(1 for kw in confirming if kw in rl)
            denying_count = sum(1 for kw in denying if kw in rl)
            is_valid = confirming_count > denying_count
            confidence = 0.8 if is_valid else 0.2
            explanation = response.split('.')[0] if '.' in response else response[:200]
            return {"valid": is_valid, "explanation": explanation, "confidence": confidence, "full_response": response[:500]}
        except Exception as e:
            logger.error(f"Validation error: {e}")
            return {"valid": False, "explanation": f"Failed: {e}", "confidence": 0.0}

    async def health(self) -> Dict[str, Any]:
        """Check health of NotebookLM connection."""
        try:
            test = await self.send_query("test", context={"health": True})
            return {"status": "healthy", "workspace_id": self.config.workspace_id, "test_response_len": len(test), "timestamp": datetime.utcnow().isoformat()}
        except Exception as e:
            return {"status": "unhealthy", "workspace_id": self.config.workspace_id, "error": str(e), "timestamp": datetime.utcnow().isoformat()}

    async def close(self) -> None:
        """Close HTTP session."""
        if self._session:
            await self._session.aclose()
            self._session = None

    def __del__(self):
        """Ensure cleanup."""
        if self._session:
            import asyncio
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    loop.create_task(self.close())
            except: pass
