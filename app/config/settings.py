from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

load_dotenv()

class Settings(BaseSettings):
    APP_NAME: str = "PriceScout Backend"

    MONGO_URI: str = os.getenv(
        "MONGO_URI",
        "mongodb+srv://uzwalabbk9_db_user:PriceScout123@cluster0.htwmjgi.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
    )

    MONGO_DB_NAME: str = os.getenv("MONGO_DB_NAME", "price_scout_db")
    DEBUG: bool = True

    class Config:
        env_file = ".env"

settings = Settings()