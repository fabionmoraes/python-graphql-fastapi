from functools import cached_property

from app.infrastructure.trino.client import TrinoClient
from app.repositories.trino.product_trino_repository import ProductTrinoRepository
from app.services.product_service import ProductService


class Container:
    def __init__(self, trino: TrinoClient) -> None:
        self.trino = trino

    @cached_property
    def _product_repository(self) -> ProductTrinoRepository:
        return ProductTrinoRepository(self.trino)

    @cached_property
    def product_service(self) -> ProductService:
        return ProductService(self._product_repository)
