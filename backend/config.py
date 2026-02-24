from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # API settings
    app_name: str = "Physical AI Textbook Chatbot"
    app_version: str = "1.0.0"

    # OpenAI settings
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4-turbo-preview"
    openai_embedding_model: str = "text-embedding-3-small"

    # Qdrant settings
    qdrant_url: Optional[str] = None
    qdrant_api_key: Optional[str] = None
    qdrant_collection_name: str = "physical_ai_textbook"

    # Database settings (Neon Postgres)
    database_url: Optional[str] = None

    # Authentication settings
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 7  # 7 days

    # Application settings
    chunk_size: int = 1000
    chunk_overlap: int = 200
    max_tokens: int = 4000

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()