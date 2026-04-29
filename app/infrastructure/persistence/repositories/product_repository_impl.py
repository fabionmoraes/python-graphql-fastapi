from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domain.entities.pagination import PageResult
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
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def list_products(
        self, where: ProductWhereEntity | None = None
    ) -> list[ProductEntity]:
        stmt = (
            select(ProductModel)
            .outerjoin(
                ProductCatalogModel,
                ProductModel.product_model_id == ProductCatalogModel.id,
            )
            .options(selectinload(ProductModel.product_model))
        )
        if where is not None:
            stmt = self._apply_string_filters(stmt, ProductModel.name, where.name)
            stmt = self._apply_string_filters(stmt, ProductModel.sku, where.sku)
            stmt = self._apply_string_filters(
                stmt, ProductCatalogModel.title, where.model_title
            )
        result = await self.db.execute(stmt)
        rows = result.scalars().unique().all()
        return [self._to_entity(row) for row in rows]

    async def list_products_paginated(
        self, first: int, after_id: int | None, where: ProductWhereEntity | None = None
    ) -> PageResult[ProductEntity]:
        base_stmt = (
            select(ProductModel)
            .outerjoin(
                ProductCatalogModel,
                ProductModel.product_model_id == ProductCatalogModel.id,
            )
        )
        if where is not None:
            base_stmt = self._apply_string_filters(base_stmt, ProductModel.name, where.name)
            base_stmt = self._apply_string_filters(base_stmt, ProductModel.sku, where.sku)
            base_stmt = self._apply_string_filters(
                base_stmt, ProductCatalogModel.title, where.model_title
            )

        count_stmt = select(func.count()).select_from(base_stmt.subquery())
        total = (await self.db.execute(count_stmt)).scalar_one()

        stmt = (
            base_stmt
            .options(selectinload(ProductModel.product_model))
            .order_by(ProductModel.id.asc())
            .limit(first + 1)
        )
        if after_id is not None:
            stmt = stmt.where(ProductModel.id > after_id)

        rows = (await self.db.execute(stmt)).scalars().unique().all()
        has_next = len(rows) > first
        entities = [self._to_entity(r) for r in rows[:first]]
        return PageResult(
            items=entities,
            total_count=total,
            has_next_page=has_next,
            has_previous_page=after_id is not None,
        )

    async def get_product_by_id(self, product_id: int) -> ProductEntity | None:
        stmt = (
            select(ProductModel)
            .where(ProductModel.id == product_id)
            .options(selectinload(ProductModel.product_model))
        )
        result = await self.db.execute(stmt)
        row = result.scalars().first()
        if row is None:
            return None
        return self._to_entity(row)

    async def list_products_by_ids(self, product_ids: list[int]) -> list[ProductEntity]:
        if not product_ids:
            return []
        stmt = (
            select(ProductModel)
            .where(ProductModel.id.in_(product_ids))
            .options(selectinload(ProductModel.product_model))
        )
        result = await self.db.execute(stmt)
        rows = result.scalars().all()
        return [self._to_entity(row) for row in rows]

    async def get_product_model_by_id(
        self, product_model_id: int
    ) -> ProductModelEntity | None:
        result = await self.db.execute(
            select(ProductCatalogModel).where(ProductCatalogModel.id == product_model_id)
        )
        row = result.scalars().first()
        if row is None:
            return None
        return ProductModelEntity(id=row.id, title=row.title)

    async def create_product(
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
        await self.db.commit()
        await self.db.refresh(row, attribute_names=["product_model"])
        return self._to_entity(row)

    @staticmethod
    def _apply_string_filters(
        stmt: Select,
        column: object,
        filter_exp: StringComparisonEntity | None,
    ) -> Select:
        if filter_exp is None:
            return stmt
        if filter_exp.eq is not None:
            stmt = stmt.where(column == filter_exp.eq)
        if filter_exp.like is not None:
            stmt = stmt.where(column.like(f"%{filter_exp.like}%"))
        if filter_exp.one_of:
            stmt = stmt.where(column.in_(filter_exp.one_of))
        return stmt

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
