import strawberry
from graphql import GraphQLError
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.infrastructure.persistence.models.product_model import ProductCatalogModel, ProductModel
from app.presentation.graphql.products.types import ProductModelType, ProductType


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
        name: str,
        price: float,
        sku: str,
        stock: int = 0,
        product_model_id: int | None = None,
    ) -> ProductType:
        db: Session = SessionLocal()
        try:
            if product_model_id is not None:
                linked_model = (
                    db.query(ProductCatalogModel)
                    .filter(ProductCatalogModel.id == product_model_id)
                    .first()
                )
                if linked_model is None:
                    raise GraphQLError("product_model_id not found.")

            row = ProductModel(
                name=name,
                price=price,
                sku=sku,
                stock=stock,
                product_model_id=product_model_id,
            )
            db.add(row)
            db.commit()
            db.refresh(row)
            return ProductMutation._to_type(row)
        finally:
            db.close()
