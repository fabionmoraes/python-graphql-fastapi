from app.domain.entities.pagination import PageResult
from app.domain.entities.product import ProductEntity, ProductWhereEntity
from app.domain.product_repository import ProductRepository


class ProductService:
    def __init__(self, repository: ProductRepository) -> None:
        self._repository = repository

    async def list_products(
        self,
        selected_fields: dict,
        first: int,
        after_id: int | None,
        where: ProductWhereEntity | None = None,
        need_total: bool = False,
    ) -> PageResult[ProductEntity]:
        return await self._repository.list_paginated(
            selected_fields=selected_fields,
            first=first,
            after_id=after_id,
            where=where,
            need_total=need_total,
        )

    async def get_product(
        self,
        product_id: int,
        selected_fields: dict,
    ) -> ProductEntity | None:
        return await self._repository.get_by_id(product_id, selected_fields)

    async def list_by_catalog_ids_grouped(
        self, catalog_ids: list[int], selected_fields: dict
    ) -> list[list[ProductEntity]]:
        products = await self._repository.list_by_catalog_ids(catalog_ids, selected_fields)

        grouped: dict[int, list[ProductEntity]] = {}
        for p in products:
            if p.product_catalog_id is not None:
                grouped.setdefault(p.product_catalog_id, []).append(p)

        return [grouped.get(cid, []) for cid in catalog_ids]
