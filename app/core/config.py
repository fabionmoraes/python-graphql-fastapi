import os
from urllib.parse import quote_plus

from dotenv import load_dotenv


load_dotenv()


class Settings:
    PROJECT_NAME = "GraphQL Estudo"
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
    JWT_SECRET = "change-me-in-production"
    JWT_ALGORITHM = "HS256"
    JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "60"))
    GRAPHQL_MAX_QUERY_DEPTH = int(os.getenv("GRAPHQL_MAX_QUERY_DEPTH", "8"))

    # Trino
    TRINO_HOST = os.getenv("TRINO_HOST", "localhost")
    TRINO_PORT = int(os.getenv("TRINO_PORT", "8080"))
    TRINO_USER = os.getenv("TRINO_USER", "trino")
    TRINO_PASSWORD = os.getenv("TRINO_PASSWORD", "")
    TRINO_CATALOG = os.getenv("TRINO_CATALOG", "")
    TRINO_SCHEMA = os.getenv("TRINO_SCHEMA", "")
    TRINO_HTTP_SCHEME = os.getenv("TRINO_HTTP_SCHEME", "http")
    TRINO_POOL_SIZE = int(os.getenv("TRINO_POOL_SIZE", "5"))

    # Tabelas — caminhos completos catalog.schema.tabela
    TRINO_TABLE_PRODUCTS = os.getenv("TRINO_TABLE_PRODUCTS", "")
    TRINO_TABLE_PRODUCT_CATALOG = os.getenv("TRINO_TABLE_PRODUCT_CATALOG", "")

    @property
    def trino_sqlalchemy_url(self) -> str:
        scheme = "trino+https" if self.TRINO_HTTP_SCHEME == "https" else "trino"
        user = quote_plus(self.TRINO_USER)
        credentials = f"{user}:{quote_plus(self.TRINO_PASSWORD)}" if self.TRINO_PASSWORD else user
        path = f"/{self.TRINO_CATALOG}" if self.TRINO_CATALOG else ""
        if path and self.TRINO_SCHEMA:
            path += f"/{self.TRINO_SCHEMA}"
        return f"{scheme}://{credentials}@{self.TRINO_HOST}:{self.TRINO_PORT}{path}"

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"


settings = Settings()
