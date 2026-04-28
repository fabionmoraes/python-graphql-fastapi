from app.domain.entities.order import OrderEntity
from app.presentation.graphql.orders.types import OrderType


def to_order_type(order: OrderEntity) -> OrderType:
    return OrderType(
        id=order.id,
        product_id=order.product_id,
        quantity=order.quantity,
        total_price=order.total_price,
    )
