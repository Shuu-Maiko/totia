from pydantic_settings import BaseSettings, SettingsConfigDict
import os

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env'), env_file_encoding='utf-8')

    DISCORD_TOKEN: str
    CHANNEL_ID: int
    GEMINI_API_KEY: str

settings = Settings()
