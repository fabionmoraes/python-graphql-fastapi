from sqlalchemy.orm import Session

from app.domain.entities.product import (
    ProductEntity,
    ProductModelEntity,
    ProductWhereEntity,
    StringComparisonEntity,
)
from app.domain.repositories.product_repository import ProductRepository
from app.infrastructure.persistence.models.product_model import (
    ProductCatalogModel,
    ProductModel,
)


class ProductRepositoryImpl(ProductRepository):
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_products(self, where: ProductWhereEntity | None = None) -> list[ProductEntity]:
        query = self.db.query(ProductModel).outerjoin(
            ProductCatalogModel,
            ProductModel.product_model_id == ProductCatalogModel.id,
        )
        if where is not None:
            query = self._apply_string_filters(query, ProductModel.name, where.name)
            query = self._apply_string_filters(query, ProductModel.sku, where.sku)
            query = self._apply_string_filters(query, ProductCatalogModel.title, where.model_title)
        rows = query.all()
        return [self._to_entity(row) for row in rows]

    def get_product_by_id(self, product_id: int) -> ProductEntity | None:
        row = self.db.query(ProductModel).filter(ProductModel.id == product_id).first()
        if row is None:
            return None
        return self._to_entity(row)

    def list_products_by_ids(self, product_ids: list[int]) -> list[ProductEntity]:
        if not product_ids:
            return []
        rows = self.db.query(ProductModel).filter(ProductModel.id.in_(product_ids)).all()
        return [self._to_entity(row) for row in rows]

    def get_product_model_by_id(self, product_model_id: int) -> ProductModelEntity | None:
        row = (
            self.db.query(ProductCatalogModel)
            .filter(ProductCatalogModel.id == product_model_id)
            .first()
        )
        if row is None:
            return None
        return ProductModelEntity(id=row.id, title=row.title)

    def create_product(
        self,
        name: str,
        price: float,
        sku: str,
        stock: int,
        product_model_id: int | None,
    ) -> ProductEntity:
        row = ProductModel(
            name=name,
            price=price,
            sku=sku,
            stock=stock,
            product_model_id=product_model_id,
        )
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return self._to_entity(row)

    @staticmethod
    def _apply_string_filters(
        query: object,
        column: object,
        filter_exp: StringComparisonEntity | None,
    ) -> object:
        if filter_exp is None:
            return query
        if filter_exp.eq is not None:
            query = query.filter(column == filter_exp.eq)
        if filter_exp.like is not None:
            query = query.filter(column.like(f"%{filter_exp.like}%"))
        if filter_exp.one_of:
            query = query.filter(column.in_(filter_exp.one_of))
        return query

    @staticmethod
    def _to_entity(row: ProductModel) -> ProductEntity:
        related = (
            ProductModelEntity(
                id=row.product_model.id,
                title=row.product_model.title,
            )
            if row.product_model
            else None
        )
        return ProductEntity(
            id=row.id,
            name=row.name,
            price=row.price,
            sku=row.sku,
            stock=row.stock,
            product_model=related,
        )
