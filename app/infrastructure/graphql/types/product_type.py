import strawberry
from strawberry.types import Info


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
class ProductCatalogType:
    id: int
    title: str

    @strawberry.field
    async def products(self, info: Info) -> list["ProductType"]:
        from app.infrastructure.graphql.types.mappers import to_product_type
        from app.infrastructure.graphql.utils.selection import parse_selected_fields

        loaders = info.context["loaders"]
        selected_fields = parse_selected_fields(info)
        entities = await loaders.get_products_by_catalog(selected_fields).load(self.id)
        return [to_product_type(p) for p in entities]


@strawberry.type
class ProductType:
    id: int
    name: str
    price: float
    sku: str
    stock: int
    product_catalog_id: int | None = None
    product_catalog: ProductCatalogType | None = None
