from pathlib import Path


class Settings:
    PROJECT_NAME = "GraphQL Estudo"
    DB_PATH = Path("db/app.db")
    DATABASE_URL = f"sqlite:///{DB_PATH}"
    JWT_SECRET = "change-me-in-production"
    JWT_ALGORITHM = "HS256"
    JWT_EXPIRE_MINUTES = 60


settings = Settings()
