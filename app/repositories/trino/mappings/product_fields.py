_PRODUCTS_TABLE = "mysql.demo.products"
_CATALOG_TABLE = "postgresql.public.product_catalog"

PRODUCT_FIELDS: dict[str, dict] = {
    "id": {
        "column": "p.id",
    },
    "name": {
        "column": "p.name",
    },
    "price": {
        "column": "p.price",
    },
    "sku": {
        "column": "p.sku",
    },
    "stock": {
        "column": "p.stock",
    },
    "productCatalogId": {
        "column": "p.product_catalog_id",
    },
    "productCatalog": {
        "join": f"LEFT JOIN {_CATALOG_TABLE} pc ON p.product_catalog_id = pc.id",
        "fields": {
            "id":    {"column": "pc.id"},
            "title": {"column": "pc.title"},
        },
    },
}
