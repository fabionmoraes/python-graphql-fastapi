import strawberry
from pydantic import ValidationError
from sqlalchemy.orm import Session
from strawberry.types import Info

from app.core.database import SessionLocal
from app.core.security import get_auth_from_header
from app.infrastructure.persistence.repositories.order_repository_impl import (
    OrderRepositoryImpl,
)
from app.presentation.graphql.orders.types import CreateOrderInput, OrderType
from app.presentation.graphql.orders.validators import CreateOrderInputValidator
from app.presentation.graphql.validation import raise_graphql_validation_error


@strawberry.type
class OrderMutation:
    @strawberry.mutation
    async def create_order(
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
            repository = OrderRepositoryImpl(db)
            order = repository.create_order(
                product_id=payload.product_id,
                quantity=payload.quantity,
                total_price=payload.total_price,
            )
            return OrderType(
                id=order.id,
                product_id=order.product_id,
                quantity=order.quantity,
                total_price=order.total_price,
            )
        finally:
            db.close()
