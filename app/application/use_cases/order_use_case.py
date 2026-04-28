from app.domain.entities.order import OrderEntity
from app.domain.repositories.order_repository import OrderRepository


class OrderUseCase:
    def __init__(self, repository: OrderRepository) -> None:
        self.repository = repository

    def list_orders(self) -> list[OrderEntity]:
        return self.repository.list_orders()

    def get_order_by_id(self, order_id: int) -> OrderEntity | None:
        return self.repository.get_order_by_id(order_id=order_id)

    def create_order(self, product_id: int, quantity: int, total_price: float) -> OrderEntity:
        return self.repository.create_order(
            product_id=product_id,
            quantity=quantity,
            total_price=total_price,
        )
