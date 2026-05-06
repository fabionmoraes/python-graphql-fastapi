from __future__ import annotations

from graphql import GraphQLError

from app.core.trino import TrinoClient
from app.domain.entities.pagination import PageResult
from app.domain.entities.product import (
    ProductEntity,
    ProductCatalogEntity,
    ProductWhereEntity,
    StringComparisonEntity,
)
from app.core.config import settings
from app.domain.repositories.product_repository import ProductRepository


def _qualified(table: str) -> str:
    parts = [p for p in [settings.TRINO_CATALOG, settings.TRINO_SCHEMA, table] if p]
    return ".".join(parts)


_PRODUCTS_TABLE = _qualified("products")
_CATALOG_TABLE = _qualified("product_catalog")

_BASE_SELECT = f"""
    SELECT
        p.id,
        p.name,
        p.price,
        p.sku,
        p.stock,
        pc.id    AS model_id,
        pc.title AS model_title
    FROM {_PRODUCTS_TABLE} p
    LEFT JOIN {_CATALOG_TABLE} pc ON p.product_catalog_id = pc.id
"""


class ProductRepositoryImpl(ProductRepository):
    def __init__(self, trino: TrinoClient) -> None:
        self._trino = trino

    async def list_products(
        self, where: ProductWhereEntity | None = None
    ) -> list[ProductEntity]:
        sql, params = self._apply_where(_BASE_SELECT, where)
        rows = await self._trino.execute(sql, params)
        return [self._to_entity(r) for r in rows]

    async def list_products_paginated(
        self,
        first: int,
        after_id: int | None,
        where: ProductWhereEntity | None = None,
    ) -> PageResult[ProductEntity]:
        count_sql = f"SELECT COUNT(*) AS total FROM {_PRODUCTS_TABLE} p LEFT JOIN {_CATALOG_TABLE} pc ON p.product_catalog_id = pc.id"
        data_sql = _BASE_SELECT

        count_sql, params = self._apply_where(count_sql, where)
        data_sql, params = self._apply_where(data_sql, where)

        if after_id is not None:
            connector = "AND" if "WHERE" in data_sql else "WHERE"
            data_sql += f" {connector} p.id > :after_id"
            params["after_id"] = after_id

        data_sql += " ORDER BY p.id ASC LIMIT :limit"
        params["limit"] = first + 1

        total_rows = await self._trino.execute(count_sql, {k: v for k, v in params.items() if k not in ("after_id", "limit")})
        total = total_rows[0]["total"] if total_rows else 0

        rows = await self._trino.execute(data_sql, params)
        has_next = len(rows) > first
        entities = [self._to_entity(r) for r in rows[:first]]

        return PageResult(
            items=entities,
            total_count=total,
            has_next_page=has_next,
            has_previous_page=after_id is not None,
        )

    async def get_product_by_id(self, product_id: int) -> ProductEntity | None:
        sql = _BASE_SELECT + " WHERE p.id = :product_id"
        rows = await self._trino.execute(sql, {"product_id": product_id})
        return self._to_entity(rows[0]) if rows else None

    async def list_products_by_ids(
        self, product_ids: list[int]
    ) -> list[ProductEntity]:
        if not product_ids:
            return []
        ids_literal = ", ".join(str(i) for i in product_ids)
        sql = _BASE_SELECT + f" WHERE p.id IN ({ids_literal})"
        rows = await self._trino.execute(sql)
        return [self._to_entity(r) for r in rows]

    async def get_product_catalog_by_id(
        self, product_catalog_id: int
    ) -> ProductCatalogEntity | None:
        sql = f"SELECT id, title FROM {_CATALOG_TABLE} WHERE id = :model_id"
        rows = await self._trino.execute(sql, {"model_id": product_catalog_id})
        if not rows:
            return None
        return ProductCatalogEntity(id=rows[0]["id"], title=rows[0]["title"])


    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _apply_where(
        sql: str,
        where: ProductWhereEntity | None,
    ) -> tuple[str, dict]:
        if where is None:
            return sql, {}

        conditions: list[str] = []
        params: dict = {}

        def _add_string_filter(
            column: str,
            prefix: str,
            flt: StringComparisonEntity | None,
        ) -> None:
            if flt is None:
                return
            if flt.eq is not None:
                conditions.append(f"{column} = :{prefix}_eq")
                params[f"{prefix}_eq"] = flt.eq
            if flt.like is not None:
                conditions.append(f"{column} LIKE :{prefix}_like")
                params[f"{prefix}_like"] = f"%{flt.like}%"
            if flt.one_of:
                escaped = ", ".join(f"'{v.replace(chr(39), chr(39)*2)}'" for v in flt.one_of)
                conditions.append(f"{column} IN ({escaped})")

        _add_string_filter("p.name", "name", where.name)
        _add_string_filter("p.sku", "sku", where.sku)
        _add_string_filter("pc.title", "model_title", where.model_title)

        if conditions:
            sql += " WHERE " + " AND ".join(conditions)

        return sql, params

    @staticmethod
    def _to_entity(row: dict) -> ProductEntity:
        model = (
            ProductCatalogEntity(id=row["model_id"], title=row["model_title"])
            if row.get("model_id") is not None
            else None
        )
        return ProductEntity(
            id=row["id"],
            name=row["name"],
            price=row["price"],
            sku=row["sku"],
            stock=row["stock"],
            product_catalog_id=row.get("model_id"),
            product_catalog=model,
        )
