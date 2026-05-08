import os

from dotenv import load_dotenv


load_dotenv()


class Settings:
    PROJECT_NAME = "GraphQL Estudo"
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
    API_USERNAME = os.getenv("API_USERNAME", "admin")
    API_PASSWORD = os.getenv("API_PASSWORD", "change-me-in-production")
    GRAPHQL_MAX_QUERY_DEPTH = int(os.getenv("GRAPHQL_MAX_QUERY_DEPTH", "8"))

    # Trino
    TRINO_HOST = os.getenv("TRINO_HOST", "localhost")
    TRINO_PORT = int(os.getenv("TRINO_PORT", "8080"))
    TRINO_USER = os.getenv("TRINO_USER", "trino")
    TRINO_PASSWORD = os.getenv("TRINO_PASSWORD", "")
    TRINO_HTTP_SCHEME = os.getenv("TRINO_HTTP_SCHEME", "http")
    TRINO_POOL_SIZE = int(os.getenv("TRINO_POOL_SIZE", "5"))

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"


settings = Settings()
