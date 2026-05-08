from typing import Protocol

from app.domain.entities.pagination import PageResult
from app.domain.entities.product import (
    ProductCatalogEntity,
    ProductEntity,
    ProductWhereEntity,
)


class ProductRepository(Protocol):
    async def list_paginated(
        self,
        selected_fields: dict,
        first: int,
        after_id: int | None,
        where: ProductWhereEntity | None = None,
        need_total: bool = False,
    ) -> PageResult[ProductEntity]: ...

    async def get_by_id(
        self, product_id: int, selected_fields: dict
    ) -> ProductEntity | None: ...

    async def list_by_ids(
        self, product_ids: list[int], selected_fields: dict
    ) -> list[ProductEntity]: ...

    async def get_catalog_by_id(
        self, product_catalog_id: int
    ) -> ProductCatalogEntity | None: ...
