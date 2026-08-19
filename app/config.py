from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    OPENAI_API_KEY: str
    OPENAI_BASE_URL: str = "https://api.groq.com/openai/v1"
    MODEL_NAME: str = "openai/gpt-oss-120b"

    DATABASE_URL: str = "sqlite:///./data/warehouse.db"
    CHROMA_PATH: str = "./data/chroma_db"
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()