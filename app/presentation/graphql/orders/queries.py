import strawberry
from strawberry.types import Info

from app.presentation.graphql.context import get_container_from_context
from app.presentation.graphql.orders.mappers import to_order_type
from app.presentation.graphql.orders.types import OrderType
from app.presentation.graphql.permissions import IsAuthenticated


@strawberry.type
class OrderQuery:
    @strawberry.field(permission_classes=[IsAuthenticated])
    async def orders(self, info: Info) -> list[OrderType]:
        container = get_container_from_context(info)
        data = await container.order_use_case.list_orders()
        return [to_order_type(order) for order in data]

    @strawberry.field(permission_classes=[IsAuthenticated])
    async def order(self, info: Info, id: int) -> OrderType | None:
        container = get_container_from_context(info)
        order = await container.order_use_case.get_order_by_id(id)
        if order is None:
            return None
        return to_order_type(order)
