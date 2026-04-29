from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.order import OrderEntity
from app.domain.repositories.order_repository import OrderRepository
from app.infrastructure.persistence.models.order_model import OrderModel


class OrderRepositoryImpl(OrderRepository):
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def list_orders(self) -> list[OrderEntity]:
        result = await self.db.execute(select(OrderModel))
        rows = result.scalars().all()
        return [self._to_entity(row) for row in rows]

    async def get_order_by_id(self, order_id: int) -> OrderEntity | None:
        result = await self.db.execute(
            select(OrderModel).where(OrderModel.id == order_id)
        )
        row = result.scalars().first()
        if row is None:
            return None
        return self._to_entity(row)

    async def create_order(
        self, product_id: int, quantity: int, total_price: float
    ) -> OrderEntity:
        row = OrderModel(product_id=product_id, quantity=quantity, total_price=total_price)
        self.db.add(row)
        await self.db.commit()
        await self.db.refresh(row)
        return self._to_entity(row)

    @staticmethod
    def _to_entity(row: OrderModel) -> OrderEntity:
        return OrderEntity(
            id=row.id,
            product_id=row.product_id,
            quantity=row.quantity,
            total_price=row.total_price,
        )
