import strawberry
from sqlalchemy.orm import Session
from strawberry.types import Info

from app.core.database import SessionLocal
from app.core.security import get_auth_from_header
from app.domain.entities.order import OrderEntity
from app.infrastructure.persistence.repositories.order_repository_impl import (
    OrderRepositoryImpl,
)
from app.presentation.graphql.orders.types import OrderType


@strawberry.type
class OrderQuery:
    @staticmethod
    def _to_type(order: OrderEntity) -> OrderType:
        return OrderType(
            id=order.id,
            product_id=order.product_id,
            quantity=order.quantity,
            total_price=order.total_price,
        )

    @strawberry.field
    def orders(self, info: Info) -> list[OrderType]:
        get_auth_from_header(info)
        db: Session = SessionLocal()
        try:
            repository = OrderRepositoryImpl(db)
            data = repository.list_orders()
            return [OrderQuery._to_type(order) for order in data]
        finally:
            db.close()

    @strawberry.field
    def order(self, info: Info, id: int) -> OrderType | None:
        get_auth_from_header(info)
        db: Session = SessionLocal()
        try:
            repository = OrderRepositoryImpl(db)
            order = repository.get_order_by_id(id)
            if order is None:
                return None
            return OrderQuery._to_type(order)
        finally:
            db.close()
