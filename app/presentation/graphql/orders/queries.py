import strawberry
from strawberry.types import Info

from app.presentation.graphql.context import get_container_from_context
from app.presentation.graphql.orders.mappers import to_order_type
from app.presentation.graphql.orders.types import OrderType
from app.presentation.graphql.pagination import (
    Connection,
    build_connection,
    decode_cursor,
)
from app.presentation.graphql.permissions import IsAuthenticated


@strawberry.type
class OrderQuery:
    @strawberry.field(permission_classes=[IsAuthenticated])
    async def orders(
        self,
        info: Info,
        first: int = 20,
        after: str | None = None,
    ) -> Connection[OrderType]:
        container = get_container_from_context(info)
        after_id = decode_cursor(after) if after else None
        page = await container.order_use_case.list_orders_paginated(
            first=first, after_id=after_id
        )
        return build_connection(page, to_order_type, lambda o: o.id)

    @strawberry.field(permission_classes=[IsAuthenticated])
    async def order(self, info: Info, id: int) -> OrderType | None:
        container = get_container_from_context(info)
        order = await container.order_use_case.get_order_by_id(id)
        if order is None:
            return None
        return to_order_type(order)
