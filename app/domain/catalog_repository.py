from typing import Protocol

from app.domain.entities.pagination import PageResult
from app.domain.entities.product import ProductCatalogEntity


class CatalogRepository(Protocol):
    async def list_paginated(
        self,
        selected_fields: dict,
        first: int,
        after_id: int | None,
        need_total: bool = False,
    ) -> PageResult[ProductCatalogEntity]: ...

    async def get_by_id(
        self, catalog_id: int, selected_fields: dict
    ) -> ProductCatalogEntity | None: ...
