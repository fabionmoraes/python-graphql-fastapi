import strawberry
from sqlalchemy.orm import Session
from strawberry.types import Info

from app.core.database import SessionLocal
from app.core.security import get_auth_from_header
from app.infrastructure.persistence.models.order_model import OrderModel
from app.presentation.graphql.orders.types import OrderType


@strawberry.type
class OrderMutation:
    @strawberry.mutation
    def create_order(
        self,
        info: Info,
        product_id: int,
        quantity: int,
        total_price: float,
    ) -> OrderType:
        get_auth_from_header(info)
        db: Session = SessionLocal()
        try:
            row = OrderModel(
                product_id=product_id,
                quantity=quantity,
                total_price=total_price,
            )
            db.add(row)
            db.commit()
            db.refresh(row)
            return OrderType(
                id=row.id,
                product_id=row.product_id,
                quantity=row.quantity,
                total_price=row.total_price,
            )
        finally:
            db.close()
