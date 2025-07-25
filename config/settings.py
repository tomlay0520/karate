from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    # Use absolute paths for database files
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))
    DATABASE_PATH: str = os.path.join(BASE_DIR, "ath.db")
    MATCH_DATABASE_PATH: str = os.path.join(BASE_DIR, "matches.db")

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'

    def __post_init__(self):
        # Ensure data directory exists
        os.makedirs(self.BASE_DIR, exist_ok=True)