"""Configuration package for BenchBuilder backend"""
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    """Application settings"""
    
    # Yahoo API
    YAHOO_CLIENT_ID: str = os.getenv("YAHOO_CLIENT_ID", "")
    YAHOO_CLIENT_SECRET: str = os.getenv("YAHOO_CLIENT_SECRET", "")
    YAHOO_REDIRECT_URI: str = os.getenv("YAHOO_REDIRECT_URI", "http://localhost:8000/auth/callback")
    
    # LLM APIs
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    
    # Application
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-this")
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./fantasy_draft.db")
    
    # Yahoo API URLs
    YAHOO_AUTH_URL = "https://api.login.yahoo.com/oauth2/request_auth"
    YAHOO_TOKEN_URL = "https://api.login.yahoo.com/oauth2/get_token"
    YAHOO_API_BASE = "https://fantasysports.yahooapis.com/fantasy/v2"

settings = Settings()
