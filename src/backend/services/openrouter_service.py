"""
OpenRouter Service - AI model communication via OpenRouter API.
"""
import httpx
from typing import Dict, Any, Optional
import json

class OpenRouterService:
    """
    Communicates with AI models through OpenRouter.
    Supports multiple model variants.
    """
    
    def __init__(self, api_key: str, default_model: str = "claude-3-opus-20240229"):
        """
        Args:
            api_key: OpenRouter API key
            default_model: Default model to use
        """
        self.api_key = api_key
        self.default_model = default_model
        self.base_url = "https://openrouter.ai/api/v1"
        self.client = httpx.AsyncClient(
            headers={
                "Authorization": f"Bearer {api_key}",
                "HTTP-Referer": "http://localhost:8000",
                "X-Title": "Nutrition AI Assistant"
            },
            timeout=httpx.Timeout(60.0)
        )
    
    async def chat_completion(
        self,
        messages: list,
        model: str = None,
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> str:
        """
        Get chat completion from AI model.
        
        Args:
            messages: List of message dicts [{"role": "user", "content": "..."}]
            model: Model ID to use
            temperature: Creativity (0-1)
            max_tokens: Max output tokens
            
        Returns:
            Response text
        """
        model_id = model or self.default_model
        
        payload = {
            "model": model_id,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        try:
            response = await self.client.post(
                f"{self.base_url}/chat/completions",
                json=payload
            )
            response.raise_for_status()
            data = response.json()
            
            return data['choices'][0]['message']['content']
            
        except httpx.HTTPError as e:
            print(f"OpenRouter API error: {e}")
            raise
        except (KeyError, IndexError) as e:
            print(f"Unexpected response format: {e}")
            raise ValueError(f"Invalid response: {response.text}")
    
    async def health(self) -> str:
        """Check connectivity."""
        try:
            response = await self.client.get(f"{self.base_url}/models")
            response.raise_for_status()
            return "healthy"
        except:
            return "unhealthy"
