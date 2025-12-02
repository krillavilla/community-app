"""
Application configuration using Pydantic Settings.
Environment variables loaded from .env file.
"""
from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field, validator


class Settings(BaseSettings):
    """Application settings from environment variables."""
    
    # Application
    PROJECT_NAME: str = "Garden Platform"
    VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api/v1"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"
    
    # Database
    DATABASE_URL: str = Field(..., description="PostgreSQL connection string")
    
    # Auth0
    AUTH0_DOMAIN: str = Field(..., description="Auth0 domain (e.g., tenant.us.auth0.com)")
    AUTH0_API_AUDIENCE: str = Field(..., description="Auth0 API audience identifier")
    AUTH0_ALGORITHMS: str = "RS256"
    AUTH0_ISSUER: str = ""  # Computed from domain
    
    # ML Service
    ML_SERVICE_URL: str = Field(default="http://ml-service:8001", description="ML service base URL")
    ML_API_KEY: str = Field(..., description="ML service API key")
    
    # R2 Storage
    R2_ACCESS_KEY_ID: str = Field(default="", description="Cloudflare R2 access key ID")
    R2_SECRET_ACCESS_KEY: str = Field(default="", description="Cloudflare R2 secret access key")
    R2_ENDPOINT_URL: str = Field(default="", description="Cloudflare R2 endpoint URL")
    R2_BUCKET_NAME: str = Field(default="garden-videos-prod", description="R2 bucket name")
    R2_PUBLIC_URL: str = Field(default="", description="R2 public URL")
    
    # Mux Video
    MUX_TOKEN_ID: str = Field(default="", description="Mux token ID")
    MUX_TOKEN_SECRET: str = Field(default="", description="Mux token secret")
    
    # CORS
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost", "http://localhost:3000"],
        description="Allowed CORS origins"
    )
    
    # Security
    SECRET_KEY: str = Field(default="change-in-production-use-openssl-rand", description="Secret key for sessions")
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    @validator("AUTH0_ISSUER", pre=True, always=True)
    def set_auth0_issuer(cls, v, values):
        """Set Auth0 issuer from domain."""
        if not v and "AUTH0_DOMAIN" in values:
            return f"https://{values['AUTH0_DOMAIN']}/"
        return v
    
    @validator("CORS_ORIGINS", pre=True)
    def parse_cors_origins(cls, v):
        """Parse CORS origins from comma-separated string or list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
