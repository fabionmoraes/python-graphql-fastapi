import strawberry
from strawberry.types import Info

from app.core.security import get_auth_from_header
from app.presentation.graphql.context import get_container_from_context
from app.presentation.graphql.orders.mappers import to_order_type
from app.presentation.graphql.orders.types import OrderType


@strawberry.type
class OrderQuery:
    @strawberry.field
    def orders(self, info: Info) -> list[OrderType]:
        get_auth_from_header(info)
        container = get_container_from_context(info)
        data = container.order_use_case.list_orders()
        return [to_order_type(order) for order in data]

    @strawberry.field
    def order(self, info: Info, id: int) -> OrderType | None:
        get_auth_from_header(info)
        container = get_container_from_context(info)
        order = container.order_use_case.get_order_by_id(id)
        if order is None:
            return None
        return to_order_type(order)
