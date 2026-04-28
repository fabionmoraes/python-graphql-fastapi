import strawberry
from pydantic import ValidationError
from strawberry.types import Info

from app.application.use_cases.product_use_case import ProductUseCase
from app.core.security import get_auth_from_header
from app.infrastructure.persistence.repositories.product_repository_impl import (
    ProductRepositoryImpl,
)
from app.presentation.graphql.context import get_db_from_context
from app.presentation.graphql.products.mappers import to_product_type
from app.presentation.graphql.products.types import CreateProductInput, ProductType
from app.presentation.graphql.products.validators import CreateProductInputValidator
from app.presentation.graphql.validation import raise_graphql_validation_error


@strawberry.type
class ProductMutation:
    @strawberry.mutation
    def create_product(
        self,
        info: Info,
        input: CreateProductInput,
    ) -> ProductType:
        try:
            payload = CreateProductInputValidator.model_validate(
                {
                    "name": input.name,
                    "price": input.price,
                    "sku": input.sku,
                    "stock": input.stock,
                    "product_model_id": input.product_model_id,
                }
            )
        except ValidationError as exc:
            raise_graphql_validation_error(exc)

        get_auth_from_header(info)
        db = get_db_from_context(info)
        repository = ProductRepositoryImpl(db)
        use_case = ProductUseCase(repository)
        product = use_case.create_product(
            name=payload.name,
            price=payload.price,
            sku=payload.sku,
            stock=payload.stock,
            product_model_id=payload.product_model_id,
        )
        return to_product_type(product)
