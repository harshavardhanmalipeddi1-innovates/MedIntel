from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    APP_NAME: str = "MedIntel"
    APP_VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api/v1"
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]
    DATABASE_URL: str = "postgresql+asyncpg://postgres:secret@localhost:5432/medintel"
    # JWT secret is loaded from .env; placeholder used in .env.example
    JWT_SECRET: str = "YOUR_GENERATED_SECRET_HERE"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24
    # Model paths (relative to project root)
    XGB_MODEL_PATH: str = "models/xgboost/model.pkl"
    XGB_FEATURE_COLUMNS_PATH: str = "models/xgboost/feature_columns.json"
    XGB_DISEASE_LABELS_PATH: str = "models/xgboost/disease_labels.json"
    KNOWLEDGE_BASE_PATH: str = "knowledge_base/"
    # AI provider configuration (environment variables)
    AI_PROVIDER: str = "vertex"
    PRIMARY_REASONING_MODEL: str = "medgemma"
    FALLBACK_REASONING_MODEL: str = "gemini"
    MODEL_VERSION: str = "latest"
    # Optional Google API key (used by Vertex AI if needed)
    GOOGLE_API_KEY: str = ""

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
