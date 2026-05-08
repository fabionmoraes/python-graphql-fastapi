from __future__ import annotations

from app.repositories.trino.mappings.catalog_fields import CATALOG_FIELDS, _CATALOG_TABLE


class CatalogQueryBuilder:
    def build(
        self,
        selected_fields: dict,
        after_id: int | None = None,
        limit: int = 100,
    ) -> tuple[str, dict]:
        columns = self._parse_fields(selected_fields)
        params: dict = {"limit": limit}

        cursor_clause = ""
        if after_id is not None:
            cursor_clause = "WHERE pc.id > :after_id"
            params["after_id"] = after_id

        sql = f"""
            SELECT {", ".join(columns)}
            FROM {_CATALOG_TABLE} pc
            {cursor_clause}
            ORDER BY pc.id ASC
            LIMIT :limit
        """
        return sql, params

    def build_count(self) -> tuple[str, dict]:
        return f"SELECT COUNT(*) AS total FROM {_CATALOG_TABLE} pc", {}

    def build_get_by_id(self, selected_fields: dict) -> str:
        columns = self._parse_fields(selected_fields)
        return f"""
            SELECT {", ".join(columns)}
            FROM {_CATALOG_TABLE} pc
            WHERE pc.id = :catalog_id
        """

    def _parse_fields(self, selected_fields: dict) -> list[str]:
        columns: list[str] = ["pc.id AS id"]
        seen = {"id"}

        for field, _ in selected_fields.items():
            config = CATALOG_FIELDS.get(field)
            if not config:
                continue
            if "column" in config and field not in seen:
                columns.append(f"{config['column']} AS {field}")
                seen.add(field)

        return columns
