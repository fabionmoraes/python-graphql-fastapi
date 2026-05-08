from app.domain.catalog_repository import CatalogRepository
from app.domain.entities.pagination import PageResult
from app.domain.entities.product import ProductCatalogEntity


class CatalogService:
    def __init__(self, repository: CatalogRepository) -> None:
        self._repository = repository

    async def list_catalogs(
        self,
        selected_fields: dict,
        first: int,
        after_id: int | None,
        need_total: bool = False,
    ) -> PageResult[ProductCatalogEntity]:
        return await self._repository.list_paginated(
            selected_fields=selected_fields,
            first=first,
            after_id=after_id,
            need_total=need_total,
        )

    async def get_catalog(
        self,
        catalog_id: int,
        selected_fields: dict,
    ) -> ProductCatalogEntity | None:
        return await self._repository.get_by_id(catalog_id, selected_fields)
