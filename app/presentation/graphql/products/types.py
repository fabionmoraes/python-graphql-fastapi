import strawberry


@strawberry.input
class StringComparisonExp:
    _eq: str | None = None
    _like: str | None = None
    _in: list[str] | None = None


@strawberry.input
class ProductWhereInput:
    name: StringComparisonExp | None = None
    sku: StringComparisonExp | None = None
    model_title: StringComparisonExp | None = None


@strawberry.type
class ProductModelType:
    id: int
    title: str


@strawberry.type
class ProductType:
    id: int
    name: str
    price: float
    sku: str
    stock: int
    product_model: ProductModelType | None = None


@strawberry.input
class CreateProductInput:
    name: str
    price: float
    sku: str
    stock: int = 0
    product_model_id: int | None = None
