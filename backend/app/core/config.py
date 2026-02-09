from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    # App settings
    APP_NAME: str = "Interview Agent"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    SECRET_KEY: str = "change_this_in_production"
    
    # Database
    DATABASE_URL: str = "postgresql://interview_agent:interview_agent_pass@localhost:5432/interview_agent"
    
    # ChromaDB
    CHROMA_DB_PATH: str = "./chroma_db"
    
    # GLM-4 API
    GLM4_API_KEY: str = ""
    GLM4_MODEL: str = "glm-4-air"
    GLM4_EMBEDDING_MODEL: str = "embedding-3"
    GLM4_BASE_URL: str = "https://open.bigmodel.cn/api/paas/v4"
    
    # LlamaParse
    LLAMAPARSE_API_KEY: Optional[str] = None
    
    # LLM Configuration
    MAX_TOKENS: int = 4096
    TEMPERATURE: float = 0.7
    
    # Retrieval Configuration
    TOP_K_RETRIEVAL: int = 5
    SIMILARITY_THRESHOLD: float = 0.7
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()
