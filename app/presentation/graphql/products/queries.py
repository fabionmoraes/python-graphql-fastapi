import strawberry
from strawberry.types import Info

from app.application.use_cases.product_use_case import ProductUseCase
from app.core.security import get_auth_from_header
from app.infrastructure.persistence.repositories.product_repository_impl import (
    ProductRepositoryImpl,
)
from app.presentation.graphql.context import get_db_from_context
from app.presentation.graphql.products.mappers import (
    to_product_type,
    to_product_where_entity,
)
from app.presentation.graphql.products.types import ProductType, ProductWhereInput


@strawberry.type
class ProductQuery:
    @strawberry.field
    def products(self, info: Info, where: ProductWhereInput | None = None) -> list[ProductType]:
        get_auth_from_header(info)
        db = get_db_from_context(info)
        repository = ProductRepositoryImpl(db)
        use_case = ProductUseCase(repository)
        data = use_case.list_products(where=to_product_where_entity(where))
        return [to_product_type(product) for product in data]

    @strawberry.field
    def product(self, info: Info, id: int) -> ProductType | None:
        get_auth_from_header(info)
        db = get_db_from_context(info)
        repository = ProductRepositoryImpl(db)
        use_case = ProductUseCase(repository)
        product = use_case.get_product_by_id(id)
        if product is None:
            return None
        return to_product_type(product)
