from dataclasses import dataclass


@dataclass
class ProductCatalogEntity:
    id: int
    title: str


@dataclass
class StringComparisonEntity:
    eq: str | None = None
    like: str | None = None
    one_of: list[str] | None = None


@dataclass
class ProductWhereEntity:
    name: StringComparisonEntity | None = None
    sku: StringComparisonEntity | None = None
    model_title: StringComparisonEntity | None = None


@dataclass
class ProductEntity:
    id: int
    name: str | None = None
    price: float | None = None
    sku: str | None = None
    stock: int | None = None
    product_catalog_id: int | None = None
    product_catalog: ProductCatalogEntity | None = None
