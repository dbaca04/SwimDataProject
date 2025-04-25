"""
Configuration Module

This module handles configuration for the application, loading settings from environment variables.
"""
import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings(BaseSettings):
    """Application settings."""
    # App Config
    APP_NAME: str = "Swimming Data API"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() in ("true", "1", "t")
    
    # Database Config
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///swim_data.db")
    
    # API Config
    API_PREFIX: str = "/api"
    CORS_ORIGINS: list = ["*"]
    
    # Security Config
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev_secret_key")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    model_config = {
        "env_file": ".env",
        "case_sensitive": True
    }


# Create global settings object
settings = Settings()
