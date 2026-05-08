from functools import cached_property

from app.infrastructure.trino.client import TrinoClient
from app.repositories.trino.catalog_trino_repository import CatalogTrinoRepository
from app.repositories.trino.product_trino_repository import ProductTrinoRepository
from app.services.catalog_service import CatalogService
from app.services.product_service import ProductService


class Container:
    def __init__(self, trino: TrinoClient) -> None:
        self.trino = trino

    @cached_property
    def _product_repository(self) -> ProductTrinoRepository:
        return ProductTrinoRepository(self.trino)

    @cached_property
    def _catalog_repository(self) -> CatalogTrinoRepository:
        return CatalogTrinoRepository(self.trino)

    @cached_property
    def product_service(self) -> ProductService:
        return ProductService(self._product_repository)

    @cached_property
    def catalog_service(self) -> CatalogService:
        return CatalogService(self._catalog_repository)
