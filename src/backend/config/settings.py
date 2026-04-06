from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

load_dotenv()

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./sqlite.db"

    # OpenRouter
    OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "")
    OPENROUTER_MODEL: str = os.getenv("OPENROUTER_MODEL", "claude-sonnet-4-20260414")
    OPENROUTER_SITE_URL: str = os.getenv("OPENROUTER_SITE_URL", "http://localhost:8000")
    OPENROUTER_SITE_NAME: str = os.getenv("OPENROUTER_SITE_NAME", "Nutrition AI Assistant")
    OPENROUTER_TIMEOUT: float = float(os.getenv("OPENROUTER_TIMEOUT", "60.0"))
    OPENROUTER_MAX_RETRIES: int = int(os.getenv("OPENROUTER_MAX_RETRIES", "3"))

    # NotebookLM / Notion
    NOTION_TOKEN: str = os.getenv("NOTION_TOKEN", "")
    NOTION_WORKSPACE: str = os.getenv("NOTION_WORKSPACE", "")
    NOTEBOOKLM_API_URL: str = os.getenv("NOTEBOOKLM_API_URL", "https://notebooklm.googleapis.com/v1")
    NOTEBOOKLM_TIMEOUT: float = float(os.getenv("NOTEBOOKLM_TIMEOUT", "30.0"))
    NOTEBOOKLM_MAX_RETRIES: int = int(os.getenv("NOTEBOOKLM_MAX_RETRIES", "3"))

    class Config:
        env_file = ".env"

settings = Settings()
