from pydantic_settings import BaseSettings, SettingsConfigDict
import os

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env'), env_file_encoding='utf-8')

    DISCORD_TOKEN: str
    CHANNEL_ID: int
    GEMINI_API_KEY: str = ""
    GROQ_API_KEY: str = ""
    LLM_PROVIDER: str = "gemini"
    LLM_MODEL: str = ""

    MEMORY_DIR: str = "data/memory"
    MEMORY_TOP_K: int = 10
    MEMORY_MIN_SCORE: float = 0.15

    # Render / HTTP Settings
    PORT: int = 8080
    RENDER_URL: str = ""

settings = Settings()
