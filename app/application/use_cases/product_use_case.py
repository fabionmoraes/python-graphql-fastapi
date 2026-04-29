from graphql import GraphQLError

from app.domain.entities.pagination import PageResult
from app.domain.entities.product import ProductEntity, ProductWhereEntity
from app.domain.repositories.product_repository import ProductRepository

_MAX_FIRST = 100


class ProductUseCase:
    def __init__(self, repository: ProductRepository) -> None:
        self.repository = repository

    async def list_products(
        self, where: ProductWhereEntity | None = None
    ) -> list[ProductEntity]:
        return await self.repository.list_products(where=where)

    async def list_products_paginated(
        self, first: int, after_id: int | None, where: ProductWhereEntity | None = None
    ) -> PageResult[ProductEntity]:
        if first < 1 or first > _MAX_FIRST:
            raise GraphQLError(f"'first' must be between 1 and {_MAX_FIRST}.")
        return await self.repository.list_products_paginated(
            first=first, after_id=after_id, where=where
        )

    async def get_product_by_id(self, product_id: int) -> ProductEntity | None:
        return await self.repository.get_product_by_id(product_id=product_id)

    async def create_product(
        self,
        name: str,
        price: float,
        sku: str,
        stock: int,
        product_model_id: int | None,
    ) -> ProductEntity:
        if product_model_id is not None:
            linked_model = await self.repository.get_product_model_by_id(product_model_id)
            if linked_model is None:
                raise GraphQLError("product_model_id not found.")

        return await self.repository.create_product(
            name=name,
            price=price,
            sku=sku,
            stock=stock,
            product_model_id=product_model_id,
        )
