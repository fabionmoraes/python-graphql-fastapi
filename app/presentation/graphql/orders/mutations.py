import strawberry
from pydantic import ValidationError
from sqlalchemy.orm import Session
from strawberry.types import Info

from app.core.database import SessionLocal
from app.core.security import get_auth_from_header
from app.infrastructure.persistence.models.order_model import OrderModel
from app.presentation.graphql.orders.types import CreateOrderInput, OrderType
from app.presentation.graphql.orders.validators import CreateOrderInputValidator
from app.presentation.graphql.validation import raise_graphql_validation_error


@strawberry.type
class OrderMutation:
    @strawberry.mutation
    def create_order(
        self,
        info: Info,
        input: CreateOrderInput,
    ) -> OrderType:
        try:
            payload = CreateOrderInputValidator.model_validate(
                {
                    "product_id": input.product_id,
                    "quantity": input.quantity,
                    "total_price": input.total_price,
                }
            )
        except ValidationError as exc:
            raise_graphql_validation_error(exc)

        get_auth_from_header(info)
        db: Session = SessionLocal()
        try:
            row = OrderModel(
                product_id=payload.product_id,
                quantity=payload.quantity,
                total_price=payload.total_price,
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
