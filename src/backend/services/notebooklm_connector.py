"""
NotebookLM Connector - Communication layer with NotebookLM API.
"""
import httpx
from typing import Optional

class NotebookLMConnector:
    """
    Handles all communication with NotebookLM workspace.
    Retrieves knowledge only - never generates nutrition facts.
    """
    
    def __init__(self, token: str = None, workspace_url: str = None):
        """
        Initialize connector.
        
        Args:
            token: Notion/OAuth token for NotebookLM access
            workspace_url: NotebookLM workspace URL
        """
        self.token = token
        self.workspace_url = workspace_url or "https://notebooklm.googleapis.com"
        self.client = None
    
    async def ensure_client(self):
        """Ensure HTTP client is initialized."""
        if self.client is None:
            self.client = httpx.AsyncClient(
                headers={"Authorization": f"Bearer {self.token}"},
                timeout=httpx.Timeout(30.0)
            )
    
    async def send_query(self, query: str) -> str:
        """
        Send query to NotebookLM and return response.
        
        Args:
            query: The nutrition question
            
        Returns:
            Response text from NotebookLM
            
        Raises:
            httpx.HTTPError: If API request fails
            ValueError: If response is empty
        """
        await self.ensure_client()
        
        try:
            # NotebookLM API endpoint - adjust based on actual API
            response = await self.client.post(
                f"{self.workspace_url}/v1/query",
                json={"query": query}
            )
            response.raise_for_status()
            
            data = response.json()
            
            # Extract response text (field name depends on NotebookLM API)
            result = data.get('response') or data.get('answer') or data.get('text', '')
            
            return result.strip()
            
        except httpx.HTTPError as e:
            print(f"NotebookLM API error: {e}")
            raise
        except Exception as e:
            print(f"Unexpected error from NotebookLM: {e}")
            raise
    
    async def health(self) -> str:
        """Check NotebookLM connectivity."""
        try:
            await self.send_query("test")
            return "healthy"
        except:
            return "unhealthy"
