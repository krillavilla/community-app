# ML Service configuration additions for app.core.config.Settings

# Add these fields to the Settings class in app/core/config.py:

"""
# ML Service Configuration
ML_SERVICE_URL: str = "http://localhost:8001"
ML_API_KEY: str = "dev-ml-key-change-in-production"
"""

# Updated Settings class with ML configuration:
"""
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://garden:garden@localhost:5432/garden_db"
    
    # Auth0
    AUTH0_DOMAIN: str
    AUTH0_API_AUDIENCE: str
    AUTH0_ALGORITHMS: str = "RS256"
    
    # ML Service
    ML_SERVICE_URL: str = "http://localhost:8001"
    ML_API_KEY: str = "dev-ml-key-change-in-production"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
"""
