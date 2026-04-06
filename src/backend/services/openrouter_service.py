"""
OpenRouter Service - AI model communication via OpenRouter API.

Provides access to multiple AI models (Claude, GPT) through a unified interface.
Handles authentication, rate limiting, retries, and error handling.

Configuration via environment variables:
    OPENROUTER_API_KEY: API key (required)
    OPENROUTER_MODEL: Default model ID
    OPENROUTER_SITE_URL: HTTP referer
    OPENROUTER_SITE_NAME: Site name
    OPENROUTER_TIMEOUT: Request timeout (seconds)
    OPENROUTER_MAX_RETRIES: Maximum retry attempts

Usage:
    service = OpenRouterService()
    response = await service.chat_completion(
        messages=[{"role": "user", "content": "Hello"}]
    )
"""
import httpx
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
from datetime import datetime
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)
import logging

from config.settings import settings

logger = logging.getLogger(__name__)


class OpenRouterConfig(BaseModel):
    """Configuration for OpenRouter service."""

    api_key: str = Field(..., description="OpenRouter API key")
    default_model: str = Field(default="claude-sonnet-4-20260414", description="Default model ID")
    site_url: str = Field(default="http://localhost:8000", description="Site URL for referer header")
    site_name: str = Field(default="Nutrition AI Assistant", description="Site name for title header")
    timeout: float = Field(default=60.0, description="Request timeout in seconds")
    max_retries: int = Field(default=3, description="Maximum retry attempts")

    @classmethod
    def from_settings(cls) -> "OpenRouterConfig":
        """Create config from application settings."""
        return cls(
            api_key=settings.OPENROUTER.api_key,
            default_model=settings.OPENROUTER.model,
            site_url=settings.OPENROUTER.site_url,
            site_name=settings.OPENROUTER.site_name,
            timeout=settings.OPENROUTER.timeout,
            max_retries=settings.OPENROUTER.max_retries,
        )


class OpenRouterMessage(BaseModel):
    """Standardized message format for chat completions."""

    role: str = Field(..., description="Message role: 'system', 'user', or 'assistant'")
    content: str = Field(..., description="Message content")


class OpenRouterResponse(BaseModel):
    """Standardized response from OpenRouter API."""

    content: str = Field(..., description="AI response content")
    model: str = Field(..., description="Model that generated the response")
    usage: Dict[str, int] = Field(default_factory=dict, description="Token usage statistics")
    finish_reason: str = Field(default="stop", description="Reason for completion")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    error: Optional[str] = Field(default=None, description="Error message if failed")

    @property
    def is_success(self) -> bool:
        """Check if response was successful."""
        return self.error is None


class OpenRouterService:
    """
    Communicates with AI models through OpenRouter API.

    Features:
    - Unified interface for multiple models (Claude, GPT)
    - Automatic retries with exponential backoff
    - Proper error handling and logging
    - Configurable timeouts

    Supported models:
    - Claude 3 (opus, sonnet, haiku)
    - GPT-4 (turbo, preview)
    - GPT-3.5-turbo
    """

    # Model groups with fallback order
    MODELS = {
        "claude": [
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307",
        ],
        "gpt": [
            "gpt-4-turbo-preview",
            "gpt-4-0125-preview",
            "gpt-3.5-turbo-0125",
        ],
    }

    def __init__(
        self,
        config: Optional[OpenRouterConfig] = None,
        api_key: Optional[str] = None,
        default_model: Optional[str] = None,
    ):
        """
        Initialize OpenRouter service.

        Args:
            config: Full configuration (takes precedence)
            api_key: API key override
            default_model: Default model override
        """
        if config:
            self.config = config
        else:
            self.config = OpenRouterConfig(
                api_key=api_key or settings.OPENROUTER.api_key,
                default_model=default_model or settings.OPENROUTER.model,
                site_url=settings.OPENROUTER.site_url,
                site_name=settings.OPENROUTER.site_name,
                timeout=settings.OPENROUTER.timeout,
                max_retries=settings.OPENROUTER.max_retries,
            )

        if not self.config.api_key:
            raise ValueError("OpenRouter API key is required. Set OPENROUTER_API_KEY environment variable.")

        self.base_url = "https://openrouter.ai/api/v1"
        self._session: Optional[httpx.AsyncClient] = None

    def _build_headers(self) -> Dict[str, str]:
        """Build required headers for OpenRouter API."""
        return {
            "Authorization": f"Bearer {self.config.api_key}",
            "HTTP-Referer": self.config.site_url,
            "X-Title": self.config.site_name,
            "Content-Type": "application/json",
        }

    async def _get_session(self) -> httpx.AsyncClient:
        """Get or create HTTP client session."""
        if self._session is None:
            self._session = httpx.AsyncClient(
                headers=self._build_headers(),
                timeout=httpx.Timeout(self.config.timeout),
            )
        return self._session

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((httpx.HTTPError, httpx.TimeoutException)),
        before_sleep=lambda retry_state: logger.warning(
            f"Retrying OpenRouter request (attempt {retry_state.attempt_number})"
        ),
    )
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        top_p: float = 1.0,
        stream: bool = False,
        **kwargs,
    ) -> OpenRouterResponse:
        """
        Get chat completion from AI model.

        Args:
            messages: List of message dicts [{"role": "user", "content": "..."}]
            model: Model ID to use (falls back to default)
            temperature: Creativity level (0.0-1.0)
            max_tokens: Maximum tokens in response
            top_p: Nucleus sampling parameter
            stream: Whether to stream response (not implemented)
            **kwargs: Additional parameters for OpenRouter

        Returns:
            OpenRouterResponse with standardized format

        Raises:
            ValueError: If API request fails
        """
        model_id = model or self.config.default_model

        payload = {
            "model": model_id,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "top_p": top_p,
            **kwargs,
        }

        try:
            session = await self._get_session()
            response = await session.post(
                f"{self.base_url}/chat/completions",
                json=payload,
            )
            response.raise_for_status()
            data = response.json()

            # Parse response
            choice = data["choices"][0]
            return OpenRouterResponse(
                content=choice["message"]["content"],
                model=data.get("model", model_id),
                usage=data.get("usage", {}),
                finish_reason=choice.get("finish_reason", "stop"),
                timestamp=datetime.utcnow(),
            )

        except httpx.HTTPStatusError as e:
            error_msg = self._parse_error_response(e)
            logger.error(error_msg)
            return OpenRouterResponse(
                content="",
                model=model_id,
                usage={},
                finish_reason="error",
                error=error_msg,
            )
        except (KeyError, IndexError) as e:
            error_msg = f"Unexpected response format: {e}"
            logger.error(error_msg)
            return OpenRouterResponse(
                content="",
                model=model_id,
                usage={},
                finish_reason="error",
                error=error_msg,
            )
        except Exception:
            raise

    def _parse_error_response(self, error: httpx.HTTPStatusError) -> str:
        """Parse error response from OpenRouter API."""
        error_msg = f"OpenRouter API error: {error.response.status_code}"
        if error.response.text:
            try:
                error_data = error.response.json()
                error_msg = f"OpenRouter error: {error_data.get('error', {}).get('message', error.response.text)}"
            except Exception:
                error_msg = error.response.text[:200]
        return error_msg

    async def simple_prompt(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
    ) -> str:
        """
        Simple text prompt interface.

        Args:
            prompt: User prompt string
            system_prompt: Optional system message
            model: Model to use
            temperature: Creativity level
            max_tokens: Max output tokens

        Returns:
            Response text or empty string on error
        """
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = await self.chat_completion(
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        return response.content if response.is_success else ""

    async def list_models(self) -> List[Dict[str, Any]]:
        """
        List available models from OpenRouter.

        Returns:
            List of model information dicts
        """
        try:
            session = await self._get_session()
            response = await session.get(f"{self.base_url}/models")
            response.raise_for_status()
            data = response.json()
            return data.get("data", [])
        except Exception as e:
            logger.error(f"Failed to list models: {e}")
            return []

    async def health(self) -> Dict[str, Any]:
        """
        Check health of OpenRouter connection.

        Returns:
            Dict with status, default_model, and timestamp
        """
        try:
            test_response = await self.simple_prompt(prompt="Hello", max_tokens=10)
            return {
                "status": "healthy" if test_response else "unhealthy",
                "default_model": self.config.default_model,
                "timestamp": datetime.utcnow().isoformat(),
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "default_model": self.config.default_model,
                "timestamp": datetime.utcnow().isoformat(),
            }

    async def close(self) -> None:
        """Close HTTP client session."""
        if self._session:
            await self._session.aclose()
            self._session = None

    def get_available_models_by_provider(self) -> Dict[str, List[str]]:
        """Get grouped model lists by provider."""
        return self.MODELS.copy()

    def is_model_available(self, model_id: str) -> bool:
        """Check if a model ID is in our supported list."""
        all_models = []
        for model_list in self.MODELS.values():
            all_models.extend(model_list)
        return model_id in all_models
