from dataclasses import dataclass


@dataclass
class ProductModelEntity:
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
    name: str
    price: float
    sku: str
    stock: int
    product_model: ProductModelEntity | None = None
