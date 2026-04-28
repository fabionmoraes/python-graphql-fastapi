import strawberry
from pydantic import ValidationError
from strawberry.types import Info

from app.application.use_cases.order_use_case import OrderUseCase
from app.core.security import get_auth_from_header
from app.infrastructure.persistence.repositories.order_repository_impl import (
    OrderRepositoryImpl,
)
from app.presentation.graphql.context import get_db_from_context
from app.presentation.graphql.orders.mappers import to_order_type
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
        db = get_db_from_context(info)
        repository = OrderRepositoryImpl(db)
        use_case = OrderUseCase(repository)
        order = use_case.create_order(
            product_id=payload.product_id,
            quantity=payload.quantity,
            total_price=payload.total_price,
        )
        return to_order_type(order)
