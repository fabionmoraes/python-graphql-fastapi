import strawberry
from strawberry.types import Info

from app.presentation.graphql.context import get_container_from_context
from app.presentation.graphql.pagination import (
    Connection,
    build_connection,
    decode_cursor,
)
from app.presentation.graphql.products.mappers import (
    to_product_type,
    to_product_where_entity,
)
from app.presentation.graphql.products.types import ProductType, ProductWhereInput


@strawberry.type
class ProductQuery:
    @strawberry.field
    async def products(
        self,
        info: Info,
        first: int = 20,
        after: str | None = None,
        where: ProductWhereInput | None = None,
    ) -> Connection[ProductType]:
        container = get_container_from_context(info)
        after_id = decode_cursor(after) if after else None
        page = await container.product_use_case.list_products_paginated(
            first=first,
            after_id=after_id,
            where=to_product_where_entity(where),
        )
        return build_connection(page, to_product_type, lambda p: p.id)

    @strawberry.field
    async def product(self, info: Info, id: int) -> ProductType | None:
        container = get_container_from_context(info)
        product = await container.product_use_case.get_product_by_id(id)
        if product is None:
            return None
        return to_product_type(product)
