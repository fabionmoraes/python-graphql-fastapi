import strawberry
from strawberry.types import Info

from app.application.use_cases.order_use_case import OrderUseCase
from app.core.security import get_auth_from_header
from app.infrastructure.persistence.repositories.order_repository_impl import (
    OrderRepositoryImpl,
)
from app.presentation.graphql.context import get_db_from_context
from app.presentation.graphql.orders.mappers import to_order_type
from app.presentation.graphql.orders.types import OrderType


@strawberry.type
class OrderQuery:
    @strawberry.field
    def orders(self, info: Info) -> list[OrderType]:
        get_auth_from_header(info)
        db = get_db_from_context(info)
        repository = OrderRepositoryImpl(db)
        use_case = OrderUseCase(repository)
        data = use_case.list_orders()
        return [to_order_type(order) for order in data]

    @strawberry.field
    def order(self, info: Info, id: int) -> OrderType | None:
        get_auth_from_header(info)
        db = get_db_from_context(info)
        repository = OrderRepositoryImpl(db)
        use_case = OrderUseCase(repository)
        order = use_case.get_order_by_id(id)
        if order is None:
            return None
        return to_order_type(order)
