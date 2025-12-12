import os
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    PROJECT_NAME: str = "Neurosymbolic Drug Repurposing Backend"
    API_V1_STR: str = ""
    
    # Security
    SECRET_KEY: str = "your-super-secret-key-for-dev"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Database
    MONGODB_URL: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "drug_repurposing_db"

    OPENAI_API_KEY: str | None = None
    GOOGLE_API_KEY: str | None = None
    
    # Paths
    # Default to the finalKG/data folder relative to the backend or absolute path
    # Assuming backend is in c:\Users\kabhi\Tesla_Curie\backend
    # and data is in c:\Users\kabhi\Tesla_Curie\finalKG\data
    KG_DATA_DIR: str = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "finalKG", "data")
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000"]

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()
