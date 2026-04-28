import strawberry
from strawberry.types import Info

from app.presentation.graphql.context import get_product_loader_from_context
from app.presentation.graphql.products.mappers import to_product_type
from app.presentation.graphql.products.types import ProductType


@strawberry.type
class OrderType:
    id: int
    product_id: int
    quantity: int
    total_price: float

    @strawberry.field
    async def product(self, info: Info) -> ProductType | None:
        loader = get_product_loader_from_context(info)
        product = await loader.load(self.product_id)
        if product is None:
            return None
        return to_product_type(product)


@strawberry.input
class CreateOrderInput:
    product_id: int
    quantity: int
    total_price: float
