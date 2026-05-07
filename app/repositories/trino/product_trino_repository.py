from __future__ import annotations

from app.domain.entities.pagination import PageResult
from app.domain.entities.product import (
    ProductCatalogEntity,
    ProductEntity,
    ProductWhereEntity,
)
from app.infrastructure.trino.client import TrinoClient
from app.query_builders.trino.product_query_builder import ProductQueryBuilder
from app.repositories.trino.mappings.product_fields import _CATALOG_TABLE, _PRODUCTS_TABLE


class ProductTrinoRepository:
    def __init__(self, trino: TrinoClient) -> None:
        self._trino = trino
        self._builder = ProductQueryBuilder()

    async def list_paginated(
        self,
        selected_fields: dict,
        first: int,
        after_id: int | None,
        where: ProductWhereEntity | None = None,
        need_total: bool = False,
    ) -> PageResult[ProductEntity]:
        sql, params = self._builder.build(selected_fields, where, after_id, first + 1)

        total = 0
        if need_total:
            count_sql, count_params = self._builder.build_count(where)
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
        self, product_id: int, selected_fields: dict
    ) -> ProductEntity | None:
        sql, params = self._builder.build(selected_fields, limit=1)
        sql = sql.replace("ORDER BY p.id ASC", "WHERE p.id = :product_id\n            ORDER BY p.id ASC")
        params["product_id"] = product_id
        rows = await self._trino.execute(sql, params)
        return self._to_entity(rows[0]) if rows else None

    async def list_by_ids(
        self, product_ids: list[int], selected_fields: dict
    ) -> list[ProductEntity]:
        if not product_ids:
            return []
        placeholders = ", ".join(f":id_{i}" for i in range(len(product_ids)))
        sql, params = self._builder.build(selected_fields, limit=len(product_ids))
        sql = sql.replace(
            "ORDER BY p.id ASC",
            f"WHERE p.id IN ({placeholders})\n            ORDER BY p.id ASC",
        )
        params.update({f"id_{i}": pid for i, pid in enumerate(product_ids)})
        rows = await self._trino.execute(sql, params)
        return [self._to_entity(r) for r in rows]

    async def get_catalog_by_id(self, product_catalog_id: int) -> ProductCatalogEntity | None:
        sql = f"SELECT id, title FROM {_CATALOG_TABLE} WHERE id = :model_id"
        rows = await self._trino.execute(sql, {"model_id": product_catalog_id})
        if not rows:
            return None
        return ProductCatalogEntity(id=rows[0]["id"], title=rows[0]["title"])

    @staticmethod
    def _to_entity(row: dict) -> ProductEntity:
        catalog_id = row.get("productCatalog_id")
        model = (
            ProductCatalogEntity(id=catalog_id, title=row["productCatalog_title"])
            if catalog_id is not None
            else None
        )
        return ProductEntity(
            id=row["id"],
            name=row.get("name"),
            price=row.get("price"),
            sku=row.get("sku"),
            stock=row.get("stock"),
            product_catalog_id=row.get("productCatalogId") or catalog_id,
            product_catalog=model,
        )
