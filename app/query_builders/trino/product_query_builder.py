from __future__ import annotations

from app.domain.entities.product import ProductWhereEntity, StringComparisonEntity
from app.repositories.trino.mappings.product_fields import (
    PRODUCT_FIELDS,
    _PRODUCTS_TABLE,
)


class ProductQueryBuilder:
    def build(
        self,
        selected_fields: dict,
        where: ProductWhereEntity | None = None,
        after_id: int | None = None,
        limit: int = 100,
    ) -> tuple[str, dict]:
        columns, joins = self._parse_fields(selected_fields, where)
        where_clause, params = self._build_where(where)

        if after_id is not None:
            connector = "AND" if where_clause else "WHERE"
            where_clause += f" {connector} p.id > :after_id"
            params["after_id"] = after_id

        params["limit"] = limit
        join_sql = "\n    ".join(joins)

        sql = f"""
            SELECT {", ".join(columns)}
            FROM {_PRODUCTS_TABLE} p
            {join_sql}
            {where_clause}
            ORDER BY p.id ASC
            LIMIT :limit
        """
        return sql, params

    def build_count(
        self,
        where: ProductWhereEntity | None = None,
    ) -> tuple[str, dict]:
        needs_join = where is not None and where.model_title is not None
        join_sql = PRODUCT_FIELDS["productCatalog"]["join"] if needs_join else ""
        where_clause, params = self._build_where(where)
        sql = f"""
            SELECT COUNT(*) AS total
            FROM {_PRODUCTS_TABLE} p
            {join_sql}
            {where_clause}
        """
        return sql, params

    def _parse_fields(
        self, selected_fields: dict, where: ProductWhereEntity | None
    ) -> tuple[list[str], list[str]]:
        columns: list[str] = ["p.id AS id"]
        joins: list[str] = []
        seen = {"id"}

        for field, value in selected_fields.items():
            config = PRODUCT_FIELDS.get(field)
            if not config:
                continue
            if "column" in config and field not in seen:
                columns.append(f"{config['column']} AS {field}")
                seen.add(field)
            if "join" in config and isinstance(value, dict):
                joins.append(config["join"])
                for subfield, _ in value.items():
                    subconfig = config.get("fields", {}).get(subfield)
                    if subconfig:
                        alias = f"{field}_{subfield}"
                        columns.append(f"{subconfig['column']} AS {alias}")

        # Join needed when filtering by catalog column even if catalog not selected
        catalog_join = PRODUCT_FIELDS["productCatalog"]["join"]
        if where and where.model_title is not None and catalog_join not in joins:
            joins.append(catalog_join)

        return columns, joins

    @staticmethod
    def _build_where(where: ProductWhereEntity | None) -> tuple[str, dict]:
        if where is None:
            return "", {}

        conditions: list[str] = []
        params: dict = {}

        def _add(column: str, prefix: str, flt: StringComparisonEntity | None) -> None:
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

        _add("p.name", "name", where.name)
        _add("p.sku", "sku", where.sku)
        _add("pc.title", "model_title", where.model_title)

        return ("WHERE " + " AND ".join(conditions)) if conditions else "", params
