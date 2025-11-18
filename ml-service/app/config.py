"""
ML Service configuration.
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """ML service settings."""
    
    # Service
    PROJECT_NAME: str = "Garden Platform ML Service"
    VERSION: str = "1.0.0"
    API_KEY: str = "dev-ml-key-12345"  # TODO: Change in production
    
    # Model paths
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    TOXICITY_MODEL: str = "unitary/toxic-bert"
    
    # Caching
    CACHE_DIR: str = "./model_cache"
    
    # Performance
    BATCH_SIZE: int = 32
    MAX_LENGTH: int = 512
    DEVICE: str = "cpu"  # or "cuda" if GPU available
    
    # Recommendations
    TOP_K_RECOMMENDATIONS: int = 10
    SIMILARITY_THRESHOLD: float = 0.3
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
