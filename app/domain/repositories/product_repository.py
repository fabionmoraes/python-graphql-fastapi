from abc import ABC, abstractmethod

from app.domain.entities.pagination import PageResult
from app.domain.entities.product import (
    ProductEntity,
    ProductCatalogEntity,
    ProductWhereEntity,
)


class ProductRepository(ABC):
    @abstractmethod
    async def list_products(
        self, where: ProductWhereEntity | None = None
    ) -> list[ProductEntity]:
        raise NotImplementedError

    @abstractmethod
    async def list_products_paginated(
        self, first: int, after_id: int | None, where: ProductWhereEntity | None = None
    ) -> PageResult[ProductEntity]:
        raise NotImplementedError

    @abstractmethod
    async def get_product_by_id(self, product_id: int) -> ProductEntity | None:
        raise NotImplementedError

    @abstractmethod
    async def list_products_by_ids(self, product_ids: list[int]) -> list[ProductEntity]:
        raise NotImplementedError

    @abstractmethod
    async def get_product_catalog_by_id(
        self, product_catalog_id: int
    ) -> ProductCatalogEntity | None:
        raise NotImplementedError

