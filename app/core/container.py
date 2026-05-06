from functools import cached_property

from app.application.use_cases.product_use_case import ProductUseCase
from app.core.trino import TrinoClient
from app.infrastructure.trino.repositories.product_repository_impl import (
    ProductRepositoryImpl,
)


class Container:
    def __init__(self, trino: TrinoClient) -> None:
        self.trino = trino

    @cached_property
    def product_use_case(self) -> ProductUseCase:
        return ProductUseCase(ProductRepositoryImpl(self.trino))
