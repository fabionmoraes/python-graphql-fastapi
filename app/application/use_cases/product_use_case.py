from graphql import GraphQLError

from app.domain.entities.product import ProductEntity, ProductWhereEntity
from app.domain.repositories.product_repository import ProductRepository


class ProductUseCase:
    def __init__(self, repository: ProductRepository) -> None:
        self.repository = repository

    def list_products(self, where: ProductWhereEntity | None = None) -> list[ProductEntity]:
        return self.repository.list_products(where=where)

    def get_product_by_id(self, product_id: int) -> ProductEntity | None:
        return self.repository.get_product_by_id(product_id=product_id)

    def create_product(
        self,
        name: str,
        price: float,
        sku: str,
        stock: int,
        product_model_id: int | None,
    ) -> ProductEntity:
        if product_model_id is not None:
            linked_model = self.repository.get_product_model_by_id(product_model_id)
            if linked_model is None:
                raise GraphQLError("product_model_id not found.")

        return self.repository.create_product(
            name=name,
            price=price,
            sku=sku,
            stock=stock,
            product_model_id=product_model_id,
        )
