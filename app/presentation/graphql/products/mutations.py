import strawberry
from graphql import GraphQLError
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.domain.entities.product import ProductEntity
from app.infrastructure.persistence.repositories.product_repository_impl import (
    ProductRepositoryImpl,
)
from app.presentation.graphql.products.types import (
    CreateProductInput,
    ProductModelType,
    ProductType,
)
from app.presentation.graphql.products.validators import CreateProductInputValidator
from app.presentation.graphql.validation import raise_graphql_validation_error


@strawberry.type
class ProductMutation:
    @staticmethod
    def _to_type(product: ProductEntity) -> ProductType:
        related = (
            ProductModelType(
                id=product.product_model.id,
                title=product.product_model.title,
            )
            if product.product_model
            else None
        )
        return ProductType(
            id=product.id,
            name=product.name,
            price=product.price,
            sku=product.sku,
            stock=product.stock,
            product_model=related,
        )

    @strawberry.mutation
    async def create_product(
        self,
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

        db: Session = SessionLocal()
        try:
            repository = ProductRepositoryImpl(db)
            if payload.product_model_id is not None:
                linked_model = repository.get_product_model_by_id(payload.product_model_id)
                if linked_model is None:
                    raise GraphQLError("product_model_id not found.")

            product = repository.create_product(
                name=payload.name,
                price=payload.price,
                sku=payload.sku,
                stock=payload.stock,
                product_model_id=payload.product_model_id,
            )
            return ProductMutation._to_type(product)
        finally:
            db.close()
