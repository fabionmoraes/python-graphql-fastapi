_CATALOG_TABLE = "postgresql.public.product_catalog"

CATALOG_FIELDS: dict[str, dict] = {
    "id":    {"column": "pc.id"},
    "title": {"column": "pc.title"},
}
