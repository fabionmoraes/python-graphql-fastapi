import os
from pathlib import Path

from dotenv import load_dotenv


load_dotenv()


class Settings:
    PROJECT_NAME = "GraphQL Estudo"
    DB_PATH = Path(os.getenv("DB_PATH", "db/app.db"))
    DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DB_PATH}")
    JWT_SECRET = "change-me-in-production"
    JWT_ALGORITHM = "HS256"
    JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "60"))


settings = Settings()
