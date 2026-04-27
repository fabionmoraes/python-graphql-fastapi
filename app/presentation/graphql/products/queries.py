import strawberry
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.infrastructure.persistence.models.product_model import ProductCatalogModel, ProductModel
from app.presentation.graphql.products.types import (
    ProductModelType,
    ProductType,
    ProductWhereInput,
    StringComparisonExp,
)


@strawberry.type
class ProductQuery:
    @staticmethod
    def _apply_string_filters(query, column, filter_exp: StringComparisonExp | None):
        if filter_exp is None:
            return query
        if filter_exp._eq is not None:
            query = query.filter(column == filter_exp._eq)
        if filter_exp._like is not None:
            query = query.filter(column.like(f"%{filter_exp._like}%"))
        if filter_exp._in:
            query = query.filter(column.in_(filter_exp._in))
        return query

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

    @strawberry.field
    def products(self, where: ProductWhereInput | None = None) -> list[ProductType]:
        db: Session = SessionLocal()
        try:
            query = db.query(ProductModel).outerjoin(
                ProductCatalogModel,
                ProductModel.product_model_id == ProductCatalogModel.id,
            )
            if where is not None:
                query = ProductQuery._apply_string_filters(query, ProductModel.name, where.name)
                query = ProductQuery._apply_string_filters(query, ProductModel.sku, where.sku)
                query = ProductQuery._apply_string_filters(
                    query,
                    ProductCatalogModel.title,
                    where.model_title,
                )
            rows = query.all()
            return [ProductQuery._to_type(row) for row in rows]
        finally:
            db.close()

    @strawberry.field
    def product(self, id: int) -> ProductType | None:
        db: Session = SessionLocal()
        try:
            row = db.query(ProductModel).filter(ProductModel.id == id).first()
            if row is None:
                return None
            return ProductQuery._to_type(row)
        finally:
            db.close()
