from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession
from strawberry.dataloader import DataLoader

from app.domain.entities.product import ProductEntity
from app.infrastructure.persistence.repositories.product_repository_impl import (
    ProductRepositoryImpl,
)


@dataclass
class Loaders:
    product_by_id: DataLoader[int, ProductEntity | None]


def create_loaders(db: AsyncSession) -> Loaders:
    product_repository = ProductRepositoryImpl(db)

    async def load_products_by_id(product_ids: list[int]) -> list[ProductEntity | None]:
        products = await product_repository.list_products_by_ids(product_ids)
        products_by_id = {product.id: product for product in products}
        return [products_by_id.get(product_id) for product_id in product_ids]

    return Loaders(
        product_by_id=DataLoader(load_fn=load_products_by_id),
    )
