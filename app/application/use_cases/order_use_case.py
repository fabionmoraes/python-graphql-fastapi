from graphql import GraphQLError

from app.domain.entities.order import OrderEntity
from app.domain.entities.pagination import PageResult
from app.domain.repositories.order_repository import OrderRepository

_MAX_FIRST = 100


class OrderUseCase:
    def __init__(self, repository: OrderRepository) -> None:
        self.repository = repository

    async def list_orders(self) -> list[OrderEntity]:
        return await self.repository.list_orders()

    async def list_orders_paginated(
        self, first: int, after_id: int | None
    ) -> PageResult[OrderEntity]:
        if first < 1 or first > _MAX_FIRST:
            raise GraphQLError(f"'first' must be between 1 and {_MAX_FIRST}.")
        return await self.repository.list_orders_paginated(first=first, after_id=after_id)

    async def get_order_by_id(self, order_id: int) -> OrderEntity | None:
        return await self.repository.get_order_by_id(order_id=order_id)

    async def create_order(
        self, product_id: int, quantity: int, total_price: float
    ) -> OrderEntity:
        return await self.repository.create_order(
            product_id=product_id,
            quantity=quantity,
            total_price=total_price,
        )
