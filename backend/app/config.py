import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "AI Recruiting Copilot"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # OpenAI & LLM Settings
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "mock-openai-key-for-local-dev")
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    PRIMARY_LLM_MODEL: str = "gpt-4o"
    REASONING_LLM_MODEL: str = "gpt-4o"
    
    # Qdrant Vector DB Settings
    QDRANT_HOST: str = os.getenv("QDRANT_HOST", "localhost")
    QDRANT_PORT: int = int(os.getenv("QDRANT_PORT", "6333"))
    QDRANT_API_KEY: str = os.getenv("QDRANT_API_KEY", "")
    QDRANT_COLLECTION: str = "candidate_resumes"
    VECTOR_DIMENSION: int = 1536
    
    # Database Settings
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "sqlite:///./recruiting_copilot.db"
    )
    
    # Operational Thresholds
    FAST_REJECT_THRESHOLD: float = 0.40  # Minimum match score required to trigger interview generation
    TOP_K_CANDIDATE_SEARCH: int = 20
    TOP_K_RESUME_CHUNKS: int = 5

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
