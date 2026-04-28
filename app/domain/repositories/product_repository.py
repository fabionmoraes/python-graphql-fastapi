from abc import ABC, abstractmethod

from app.domain.entities.product import (
    ProductEntity,
    ProductModelEntity,
    ProductWhereEntity,
)


class ProductRepository(ABC):
    @abstractmethod
    def list_products(self, where: ProductWhereEntity | None = None) -> list[ProductEntity]:
        raise NotImplementedError

    @abstractmethod
    def get_product_by_id(self, product_id: int) -> ProductEntity | None:
        raise NotImplementedError

    @abstractmethod
    def get_product_model_by_id(self, product_model_id: int) -> ProductModelEntity | None:
        raise NotImplementedError

    @abstractmethod
    def create_product(
        self,
        name: str,
        price: float,
        sku: str,
        stock: int,
        product_model_id: int | None,
    ) -> ProductEntity:
        raise NotImplementedError
