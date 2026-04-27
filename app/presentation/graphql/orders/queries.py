import strawberry
from sqlalchemy.orm import Session

from app.core.security import get_auth_from_header
from app.core.database import SessionLocal
from app.infrastructure.persistence.models.order_model import OrderModel
from app.presentation.graphql.orders.types import OrderType
from strawberry.types import Info


@strawberry.type
class OrderQuery:
    @strawberry.field
    def orders(self, info: Info) -> list[OrderType]:
        get_auth_from_header(info)
        db: Session = SessionLocal()
        try:
            rows = db.query(OrderModel).all()
            return [
                OrderType(
                    id=row.id,
                    product_id=row.product_id,
                    quantity=row.quantity,
                    total_price=row.total_price,
                )
                for row in rows
            ]
        finally:
            db.close()

    @strawberry.field
    def order(self, info: Info, id: int) -> OrderType | None:
        get_auth_from_header(info)
        db: Session = SessionLocal()
        try:
            row = db.query(OrderModel).filter(OrderModel.id == id).first()
            if row is None:
                return None
            return OrderType(
                id=row.id,
                product_id=row.product_id,
                quantity=row.quantity,
                total_price=row.total_price,
            )
        finally:
            db.close()
