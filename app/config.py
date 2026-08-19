from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    OPENAI_API_KEY: str = "your-openai-key-here"   # ya Grok/xAI compatible key
    OPENAI_BASE_URL: str = "https://api.openai.com/v1"  # change if using Grok/xAI
    MODEL_NAME: str = "gpt-4o-mini"
    DATABASE_URL: str = "sqlite:///./data/warehouse.db"
    CHROMA_PATH: str = "./data/chroma_db"
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"

    class Config:
        env_file = ".env"

settings = Settings()