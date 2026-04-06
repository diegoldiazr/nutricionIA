"""
OpenRouter Service - AI model communication via OpenRouter API.

Responsibilities:
- Send prompts to AI models
- Select and switch between models
- Return responses with proper error handling
- Support multiple model variants (Claude, GPT, etc.)

Configuration via environment variables:
- OPENROUTER_API_KEY: API key for OpenRouter
- OPENROUTER_MODEL: Default model (e.g., "claude-3-opus-20240229")
- OPENROUTER_SITE_URL: HTTP referer for API requests
- OPENROUTER_SITE_NAME: Site name for API requests
"""
import os
import httpx
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
from datetime import datetime
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import logging

logger = logging.getLogger(__name__)


class OpenRouterConfig(BaseModel):
    """Configuration for OpenRouter service."""
    api_key: str = Field(..., description="OpenRouter API key")
    default_model: str = Field("claude-3-opus-20240229", description="Default model ID")
    site_url: str = Field("http://localhost:8000", description="Site URL for referer header")
    site_name: str = Field("Nutrition AI Assistant", description="Site name for title header")
    timeout: float = Field(60.0, description="Request timeout in seconds")
    max_retries: int = Field(3, description="Maximum retry attempts for failed requests")


class OpenRouterMessage(BaseModel):
    """Standardized message format for chat completions."""
    role: str  # "system", "user", "assistant"
    content: str


class OpenRouterResponse(BaseModel):
    """Standardized response from OpenRouter."""
    content: str
    model: str
    usage: Dict[str, int] = {}
    finish_reason: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    error: Optional[str] = None


class OpenRouterService:
    """
    Communicates with AI models through OpenRouter.
    Handles model selection, prompt formatting, and response parsing.
    """

    # Supported models with fallback order
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
        config: OpenRouterConfig = None,
        api_key: str = None,
        default_model: str = None,
    ):
        """
        Initialize OpenRouter service.

        Args:
            config: Full configuration object (takes precedence)
            api_key: API key (will load from env if None)
            default_model: Default model (will load from env if None)
        """
        # Load configuration
        if config:
            self.config = config
        else:
            self.config = OpenRouterConfig(
                api_key=api_key or os.getenv("OPENROUTER_API_KEY", ""),
                default_model=default_model or os.getenv("OPENROUTER_MODEL", "claude-3-opus-20240229"),
                site_url=os.getenv("OPENROUTER_SITE_URL", "http://localhost:8000"),
                site_name=os.getenv("OPENROUTER_SITE_NAME", "Nutrition AI Assistant"),
                timeout=float(os.getenv("OPENROUTER_TIMEOUT", "60.0")),
                max_retries=int(os.getenv("OPENROUTER_MAX_RETRIES", "3")),
            )

        if not self.config.api_key:
            raise ValueError("OpenRouter API key is required. Set OPENROUTER_API_KEY environment variable.")

        self.base_url = "https://openrouter.ai/api/v1"
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
        """Build required headers for OpenRouter API."""
        return {
            "Authorization": f"Bearer {self.config.api_key}",
            "HTTP-Referer": self.config.site_url,
            "X-Title": self.config.site_name,
            "Content-Type": "application/json",
        }

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((httpx.HTTPError, httpx.TimeoutException)),
        before_sleep=lambda retry_state: logger.warning(f"Retrying OpenRouter request (attempt {retry_state.attempt_number})")
    )
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        top_p: float = 1.0,
        stream: bool = False,
        **kwargs
    ) -> OpenRouterResponse:
        """
        Get chat completion from AI model.

        Args:
            messages: List of message dicts [{"role": "user", "content": "..."}]
            model: Model ID to use (falls back to default)
            temperature: Creativity (0-1)
            max_tokens: Maximum tokens in response
            top_p: Nucleus sampling parameter
            stream: Whether to stream response (not implemented)
            **kwargs: Additional parameters for OpenRouter

        Returns:
            OpenRouterResponse with standardized format
        """
        model_id = model or self.config.default_model

        payload = {
            "model": model_id,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "top_p": top_p,
            **kwargs
        }

        try:
            session = await self.ensure_session()
            response = await session.post(
                f"{self.base_url}/chat/completions",
                json=payload
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
                timestamp=datetime.utcnow()
            )

        except httpx.HTTPStatusError as e:
            error_msg = f"OpenRouter API error: {e.response.status_code}"
            if e.response.text:
                try:
                    error_data = e.response.json()
                    error_msg = f"OpenRouter error: {error_data.get('error', {}).get('message', e.response.text)}"
                except:
                    error_msg = e.response.text[:200]
            logger.error(error_msg)
            return OpenRouterResponse(
                content="",
                model=model_id,
                usage={},
                finish_reason="error",
                error=error_msg
            )
        except (KeyError, IndexError) as e:
            logger.error(f"Unexpected response format: {e}")
            return OpenRouterResponse(
                content="",
                model=model_id,
                usage={},
                finish_reason="error",
                error=f"Invalid response format: {str(e)}"
            )
        except Exception as e:
            logger.exception(f"Unexpected error in chat_completion: {e}")
            raise

    async def simple_prompt(
        self,
        prompt: str,
        system_prompt: str = None,
        model: str = None,
        temperature: float = 0.7,
        max_tokens: int = 1000
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
            max_tokens=max_tokens
        )

        return response.content if not response.error else ""

    async def list_models(self) -> List[Dict[str, Any]]:
        """
        List available models from OpenRouter.

        Returns:
            List of model information dicts
        """
        try:
            session = await self.ensure_session()
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
            # Simple test request
            test_response = await self.simple_prompt(
                prompt="Hello",
                max_tokens=10
            )
            return {
                "status": "healthy" if test_response else "unhealthy",
                "default_model": self.config.default_model,
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "default_model": self.config.default_model,
                "timestamp": datetime.utcnow().isoformat()
            }

    async def close(self) -> None:
        """Close HTTP client session."""
        if self._session:
            await self._session.aclose()
            self._session = None

    def get_available_models_by_provider(self) -> Dict[str, List[str]]:
        """
        Get grouped model lists by provider.

        Returns:
            Dict mapping provider names to model ID lists
        """
        return self.MODELS.copy()

    def is_model_available(self, model_id: str) -> bool:
        """
        Check if a model ID is in our supported list.

        Args:
            model_id: Model identifier to check

        Returns:
            True if model is in supported list
        """
        all_models = []
        for model_list in self.MODELS.values():
            all_models.extend(model_list)
        return model_id in all_models
