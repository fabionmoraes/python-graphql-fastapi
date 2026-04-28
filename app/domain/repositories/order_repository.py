from abc import ABC, abstractmethod

from app.domain.entities.order import OrderEntity


class OrderRepository(ABC):
    @abstractmethod
    def list_orders(self) -> list[OrderEntity]:
        raise NotImplementedError

    @abstractmethod
    def get_order_by_id(self, order_id: int) -> OrderEntity | None:
        raise NotImplementedError

    @abstractmethod
    def create_order(self, product_id: int, quantity: int, total_price: float) -> OrderEntity:
        raise NotImplementedError
