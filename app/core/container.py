from functools import cached_property

from app.infrastructure.trino.ibis_client import IbisClient
from app.infrastructure.trino.repositories.catalog_repository_impl import CatalogTrinoRepository
from app.infrastructure.trino.repositories.product_repository_impl import ProductTrinoRepository
from app.services.catalog_service import CatalogService
from app.services.product_service import ProductService


class Container:
    def __init__(self, client: IbisClient) -> None:
        self._client = client

    @cached_property
    def _product_repository(self) -> ProductTrinoRepository:
        return ProductTrinoRepository(self._client)

    @cached_property
    def _catalog_repository(self) -> CatalogTrinoRepository:
        return CatalogTrinoRepository(self._client)

    @cached_property
    def product_service(self) -> ProductService:
        return ProductService(self._product_repository)

    @cached_property
    def catalog_service(self) -> CatalogService:
        return CatalogService(self._catalog_repository)
