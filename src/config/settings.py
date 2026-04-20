"""Settings configuration."""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3:latest "
    ollama_embedding_model: str = "nomic-embed-text"
    n8n_webhook_secret: str
    telegram_bot_token: str
    chroma_path: str = "./chroma_db"
    slack_webhook_url: Optional[str] = None  # for escalation

    class Config:
        env_file = ".env"


settings = Settings()
