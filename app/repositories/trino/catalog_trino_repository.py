from __future__ import annotations

from app.domain.entities.pagination import PageResult
from app.domain.entities.product import ProductCatalogEntity
from app.infrastructure.trino.client import TrinoClient
from app.query_builders.trino.catalog_query_builder import CatalogQueryBuilder


class CatalogTrinoRepository:
    def __init__(self, trino: TrinoClient) -> None:
        self._trino = trino
        self._builder = CatalogQueryBuilder()

    async def list_paginated(
        self,
        selected_fields: dict,
        first: int,
        after_id: int | None,
        need_total: bool = False,
    ) -> PageResult[ProductCatalogEntity]:
        sql, params = self._builder.build(selected_fields, after_id, first + 1)

        total = 0
        if need_total:
            count_sql, count_params = self._builder.build_count()
            total_rows = await self._trino.execute(count_sql, count_params)
            total = total_rows[0]["total"] if total_rows else 0

        rows = await self._trino.execute(sql, params)
        has_next = len(rows) > first
        entities = [self._to_entity(r) for r in rows[:first]]

        return PageResult(
            items=entities,
            total_count=total,
            has_next_page=has_next,
            has_previous_page=after_id is not None,
        )

    async def get_by_id(
        self, catalog_id: int, selected_fields: dict
    ) -> ProductCatalogEntity | None:
        sql = self._builder.build_get_by_id(selected_fields)
        rows = await self._trino.execute(sql, {"catalog_id": catalog_id})
        return self._to_entity(rows[0]) if rows else None

    @staticmethod
    def _to_entity(row: dict) -> ProductCatalogEntity:
        return ProductCatalogEntity(
            id=row["id"],
            title=row.get("title"),
        )
