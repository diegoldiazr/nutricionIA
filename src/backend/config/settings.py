from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

load_dotenv()

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./sqlite.db"
    OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "")
    NOTION_TOKEN: str = os.getenv("NOTION_TOKEN", "")
    NOTION_WORKSPACE: str = os.getenv("NOTION_WORKSPACE", "")
    
    class Config:
        env_file = ".env"

settings = Settings()
