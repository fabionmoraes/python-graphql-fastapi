import strawberry
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.domain.entities.product import (
    ProductEntity,
    ProductWhereEntity,
    StringComparisonEntity,
)
from app.infrastructure.persistence.repositories.product_repository_impl import (
    ProductRepositoryImpl,
)
from app.presentation.graphql.products.types import (
    ProductModelType,
    ProductType,
    ProductWhereInput,
    StringComparisonExp,
)


@strawberry.type
class ProductQuery:
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

    @staticmethod
    def _to_string_comparison(filter_exp: StringComparisonExp | None) -> StringComparisonEntity | None:
        if filter_exp is None:
            return None
        return StringComparisonEntity(
            eq=filter_exp._eq,
            like=filter_exp._like,
            one_of=filter_exp._in,
        )

    @staticmethod
    def _to_where_entity(where: ProductWhereInput | None) -> ProductWhereEntity | None:
        if where is None:
            return None
        return ProductWhereEntity(
            name=ProductQuery._to_string_comparison(where.name),
            sku=ProductQuery._to_string_comparison(where.sku),
            model_title=ProductQuery._to_string_comparison(where.model_title),
        )

    @strawberry.field
    def products(self, where: ProductWhereInput | None = None) -> list[ProductType]:
        db: Session = SessionLocal()
        try:
            repository = ProductRepositoryImpl(db)
            data = repository.list_products(ProductQuery._to_where_entity(where))
            return [ProductQuery._to_type(product) for product in data]
        finally:
            db.close()

    @strawberry.field
    def product(self, id: int) -> ProductType | None:
        db: Session = SessionLocal()
        try:
            repository = ProductRepositoryImpl(db)
            product = repository.get_product_by_id(id)
            if product is None:
                return None
            return ProductQuery._to_type(product)
        finally:
            db.close()
