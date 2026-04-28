from sqlalchemy.orm import Session
from strawberry.dataloader import DataLoader

from app.domain.entities.product import ProductEntity
from app.infrastructure.persistence.repositories.product_repository_impl import (
    ProductRepositoryImpl,
)


def create_product_by_id_loader(db: Session) -> DataLoader[int, ProductEntity | None]:
    async def batch_load_fn(product_ids: list[int]) -> list[ProductEntity | None]:
        repository = ProductRepositoryImpl(db)
        products = repository.list_products_by_ids(product_ids)
        products_by_id = {product.id: product for product in products}
        return [products_by_id.get(product_id) for product_id in product_ids]

    return DataLoader(load_fn=batch_load_fn)
