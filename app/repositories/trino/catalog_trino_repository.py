from __future__ import annotations

from app.domain.entities.pagination import PageResult
from app.domain.entities.product import ProductCatalogEntity
from app.infrastructure.trino.ibis_client import IbisClient

_CATALOG_DB: tuple[str, str] = ("postgresql", "public")


class CatalogTrinoRepository:
    def __init__(self, client: IbisClient) -> None:
        self._client = client
        self._catalogs = client.table("product_catalog", database=_CATALOG_DB)

    async def list_paginated(
        self,
        selected_fields: dict,
        first: int,
        after_id: int | None,
        need_total: bool = False,
    ) -> PageResult[ProductCatalogEntity]:
        c = self._catalogs

        total = 0
        if need_total:
            total = int(await self._client.execute_scalar(c.count()))

        base = c.filter(c["id"] > after_id) if after_id is not None else c
        expr = (
            base.select(self._columns(selected_fields))
            .order_by("id")
            .limit(first + 1)
        )

        rows = await self._client.execute(expr)
        has_next = len(rows) > first

        return PageResult(
            items=[self._to_entity(r) for r in rows[:first]],
            total_count=total,
            has_next_page=has_next,
            has_previous_page=after_id is not None,
        )

    async def get_by_id(
        self, catalog_id: int, selected_fields: dict
    ) -> ProductCatalogEntity | None:
        c = self._catalogs
        expr = (
            c.filter(c["id"] == catalog_id)
            .select(self._columns(selected_fields))
            .limit(1)
        )
        rows = await self._client.execute(expr)
        return self._to_entity(rows[0]) if rows else None

    def _columns(self, selected_fields: dict) -> list:
        c = self._catalogs
        cols = [c["id"]]
        if "title" in selected_fields:
            cols.append(c["title"])
        return cols

    @staticmethod
    def _to_entity(row: dict) -> ProductCatalogEntity:
        return ProductCatalogEntity(id=row["id"], title=row.get("title"))
