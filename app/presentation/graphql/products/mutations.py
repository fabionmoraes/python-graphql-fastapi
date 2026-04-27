import strawberry
from graphql import GraphQLError
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.infrastructure.persistence.models.product_model import ProductCatalogModel, ProductModel
from app.presentation.graphql.products.types import CreateProductInput, ProductModelType, ProductType
from app.presentation.graphql.products.validators import CreateProductInputValidator
from app.presentation.graphql.validation import raise_graphql_validation_error


@strawberry.type
class ProductMutation:
    @staticmethod
    def _to_type(row: ProductModel) -> ProductType:
        related = (
            ProductModelType(
                id=row.product_model.id,
                title=row.product_model.title,
            )
            if row.product_model
            else None
        )
        return ProductType(
            id=row.id,
            name=row.name,
            price=row.price,
            sku=row.sku,
            stock=row.stock,
            product_model=related,
        )

    @strawberry.mutation
    def create_product(
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
            if payload.product_model_id is not None:
                linked_model = (
                    db.query(ProductCatalogModel)
                    .filter(ProductCatalogModel.id == payload.product_model_id)
                    .first()
                )
                if linked_model is None:
                    raise GraphQLError("product_model_id not found.")

            row = ProductModel(
                name=payload.name,
                price=payload.price,
                sku=payload.sku,
                stock=payload.stock,
                product_model_id=payload.product_model_id,
            )
            db.add(row)
            db.commit()
            db.refresh(row)
            return ProductMutation._to_type(row)
        finally:
            db.close()
