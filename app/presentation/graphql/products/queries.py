import strawberry
from strawberry.types import Info

from app.core.security import get_auth_from_header
from app.presentation.graphql.context import get_container_from_context
from app.presentation.graphql.products.mappers import (
    to_product_type,
    to_product_where_entity,
)
from app.presentation.graphql.products.types import ProductType, ProductWhereInput


@strawberry.type
class ProductQuery:
    @strawberry.field
    def products(self, info: Info, where: ProductWhereInput | None = None) -> list[ProductType]:
        get_auth_from_header(info)
        container = get_container_from_context(info)
        data = container.product_use_case.list_products(where=to_product_where_entity(where))
        return [to_product_type(product) for product in data]

    @strawberry.field
    def product(self, info: Info, id: int) -> ProductType | None:
        get_auth_from_header(info)
        container = get_container_from_context(info)
        product = container.product_use_case.get_product_by_id(id)
        if product is None:
            return None
        return to_product_type(product)
