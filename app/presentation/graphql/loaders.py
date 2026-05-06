from dataclasses import dataclass

from strawberry.dataloader import DataLoader

from app.core.trino import TrinoClient
from app.domain.entities.product import ProductEntity
from app.infrastructure.trino.repositories.product_repository_impl import (
    ProductRepositoryImpl,
)


@dataclass
class Loaders:
    product_by_id: DataLoader[int, ProductEntity | None]


def create_loaders(trino: TrinoClient) -> Loaders:
    product_repository = ProductRepositoryImpl(trino)

    async def load_products_by_id(
        product_ids: list[int],
    ) -> list[ProductEntity | None]:
        products = await product_repository.list_products_by_ids(product_ids)
        products_by_id = {p.id: p for p in products}
        return [products_by_id.get(pid) for pid in product_ids]

    return Loaders(
        product_by_id=DataLoader(load_fn=load_products_by_id),
    )
