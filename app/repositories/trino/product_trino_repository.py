from __future__ import annotations

import ibis.expr.types as ir

from app.domain.entities.pagination import PageResult
from app.domain.entities.product import (
    ProductCatalogEntity,
    ProductEntity,
    ProductWhereEntity,
)
from app.infrastructure.trino.ibis_client import IbisClient

_PRODUCTS_DB: tuple[str, str] = ("mysql", "demo")
_CATALOG_DB: tuple[str, str] = ("postgresql", "public")


class ProductTrinoRepository:
    def __init__(self, client: IbisClient) -> None:
        self._client = client
        self._products = client.table("products", database=_PRODUCTS_DB)
        self._catalogs = client.table("product_catalog", database=_CATALOG_DB)

    async def list_paginated(
        self,
        selected_fields: dict,
        first: int,
        after_id: int | None,
        where: ProductWhereEntity | None = None,
        need_total: bool = False,
    ) -> PageResult[ProductEntity]:
        total = 0
        if need_total:
            total = int(await self._client.execute_scalar(self._count_expr(where)))

        expr = self._build_expr(selected_fields, where, after_id, limit=first + 1)
        rows = await self._client.execute(expr)
        has_next = len(rows) > first

        return PageResult(
            items=[self._to_entity(r) for r in rows[:first]],
            total_count=total,
            has_next_page=has_next,
            has_previous_page=after_id is not None,
        )

    async def get_by_id(
        self, product_id: int, selected_fields: dict
    ) -> ProductEntity | None:
        p = self._products
        expr = self._build_expr(
            selected_fields, limit=1, extra=[p["id"] == product_id]
        )
        rows = await self._client.execute(expr)
        return self._to_entity(rows[0]) if rows else None

    async def list_by_ids(
        self, product_ids: list[int], selected_fields: dict
    ) -> list[ProductEntity]:
        if not product_ids:
            return []
        p = self._products
        expr = self._build_expr(selected_fields, extra=[p["id"].isin(product_ids)])
        rows = await self._client.execute(expr)
        return [self._to_entity(r) for r in rows]

    async def list_by_catalog_ids(
        self, catalog_ids: list[int], selected_fields: dict
    ) -> list[ProductEntity]:
        if not catalog_ids:
            return []
        p = self._products
        expr = self._build_expr(
            selected_fields, extra=[p["product_catalog_id"].isin(catalog_ids)]
        )
        rows = await self._client.execute(expr)
        return [self._to_entity(r) for r in rows]

    async def get_catalog_by_id(
        self, product_catalog_id: int
    ) -> ProductCatalogEntity | None:
        c = self._catalogs
        expr = (
            c.filter(c["id"] == product_catalog_id)
            .select([c["id"], c["title"]])
            .limit(1)
        )
        rows = await self._client.execute(expr)
        if not rows:
            return None
        return ProductCatalogEntity(id=rows[0]["id"], title=rows[0]["title"])

    # ------------------------------------------------------------------
    # internal builders
    # ------------------------------------------------------------------

    def _build_expr(
        self,
        selected_fields: dict,
        where: ProductWhereEntity | None = None,
        after_id: int | None = None,
        limit: int | None = None,
        extra: list | None = None,
    ) -> ir.Table:
        p = self._products
        c = self._catalogs
        needs_select = "productCatalog" in selected_fields
        needs_join = needs_select or (
            where is not None and where.model_title is not None
        )

        base: ir.Table = (
            p.join(c, p["product_catalog_id"] == c["id"], how="left")
            if needs_join
            else p
        )

        predicates = self._predicates(where, after_id)
        if extra:
            predicates.extend(extra)
        if predicates:
            base = base.filter(predicates)

        expr = base.select(self._columns(selected_fields, needs_select)).order_by("id")
        if limit is not None:
            expr = expr.limit(limit)
        return expr

    def _count_expr(self, where: ProductWhereEntity | None) -> ir.Scalar:
        p = self._products
        c = self._catalogs
        needs_join = where is not None and where.model_title is not None
        base: ir.Table = (
            p.join(c, p["product_catalog_id"] == c["id"], how="left")
            if needs_join
            else p
        )
        predicates = self._predicates(where, after_id=None)
        if predicates:
            base = base.filter(predicates)
        return base.count()

    def _predicates(
        self,
        where: ProductWhereEntity | None,
        after_id: int | None,
    ) -> list:
        p = self._products
        c = self._catalogs
        preds = []

        if after_id is not None:
            preds.append(p["id"] > after_id)

        if where is None:
            return preds

        for col, flt in [
            (p["name"], where.name),
            (p["sku"], where.sku),
        ]:
            if flt is None:
                continue
            if flt.eq is not None:
                preds.append(col == flt.eq)
            if flt.like is not None:
                preds.append(col.like(f"%{flt.like}%"))
            if flt.one_of:
                preds.append(col.isin(flt.one_of))

        if where.model_title is not None:
            mt = where.model_title
            if mt.eq is not None:
                preds.append(c["title"] == mt.eq)
            if mt.like is not None:
                preds.append(c["title"].like(f"%{mt.like}%"))
            if mt.one_of:
                preds.append(c["title"].isin(mt.one_of))

        return preds

    def _columns(self, selected_fields: dict, needs_catalog_select: bool) -> list:
        p = self._products
        c = self._catalogs

        cols = [p["id"], p["product_catalog_id"].name("productCatalogId")]
        seen = {"id", "productCatalogId"}

        for field in selected_fields:
            if field in seen:
                continue
            if field == "name":
                cols.append(p["name"])
            elif field == "price":
                cols.append(p["price"])
            elif field == "sku":
                cols.append(p["sku"])
            elif field == "stock":
                cols.append(p["stock"])
            elif field == "productCatalog" and needs_catalog_select:
                sub = selected_fields[field]
                if isinstance(sub, dict):
                    if "id" in sub:
                        cols.append(c["id"].name("productCatalog_id"))
                    if "title" in sub:
                        cols.append(c["title"].name("productCatalog_title"))
            seen.add(field)

        return cols

    @staticmethod
    def _to_entity(row: dict) -> ProductEntity:
        catalog_id = row.get("productCatalog_id")
        model = (
            ProductCatalogEntity(
                id=catalog_id, title=row.get("productCatalog_title")
            )
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
