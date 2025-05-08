
import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Cargar variables de entorno desde el archivo .env
load_dotenv()

class Settings(BaseSettings):
    DB_HOST: str = os.getenv("DB_HOST", "db")
    DB_PORT: str = os.getenv("DB_PORT", "5432")
    DB_NAME: str = os.getenv("DB_NAME", "cliniccloud")
    DB_USER: str = os.getenv("DB_USER", "admin")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "admin123")
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )
    
    EMBEDDING_MODEL: str = os.getenv(
        "EMBEDDING_MODEL", 
        "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    )
    EMBEDDING_DIMENSION: int = int(os.getenv("EMBEDDING_DIMENSION", "768"))
    SIMILARITY_THRESHOLD: float = float(os.getenv("SIMILARITY_THRESHOLD", "0.5"))
    MAX_SEARCH_RESULTS: int = int(os.getenv("MAX_SEARCH_RESULTS", "20"))
    
    MODEL_CACHE_DIR: str = os.getenv("MODEL_CACHE_DIR", "/app/models")
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        
# crear una instancia de settings
settings = Settings()
