import strawberry
from strawberry.types import Info

from app.presentation.graphql.context import get_container_from_context
from app.presentation.graphql.permissions import IsAuthenticated
from app.presentation.graphql.products.mappers import (
    to_product_type,
    to_product_where_entity,
)
from app.presentation.graphql.products.types import ProductType, ProductWhereInput


@strawberry.type
class ProductQuery:
    @strawberry.field(permission_classes=[IsAuthenticated])
    async def products(
        self, info: Info, where: ProductWhereInput | None = None
    ) -> list[ProductType]:
        container = get_container_from_context(info)
        data = await container.product_use_case.list_products(
            where=to_product_where_entity(where)
        )
        return [to_product_type(product) for product in data]

    @strawberry.field(permission_classes=[IsAuthenticated])
    async def product(self, info: Info, id: int) -> ProductType | None:
        container = get_container_from_context(info)
        product = await container.product_use_case.get_product_by_id(id)
        if product is None:
            return None
        return to_product_type(product)
