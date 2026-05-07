from functools import cached_property

from app.core.trino import TrinoClient
from app.infrastructure.trino.repositories.product_repository_impl import (
    ProductRepositoryImpl,
)


class Container:
    def __init__(self, trino: TrinoClient) -> None:
        self.trino = trino

    @cached_property
    def product_repository(self) -> ProductRepositoryImpl:
        return ProductRepositoryImpl(self.trino)
