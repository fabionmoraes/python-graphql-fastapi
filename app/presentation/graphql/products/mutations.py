import strawberry
from pydantic import ValidationError
from strawberry.types import Info

from app.presentation.graphql.context import get_container_from_context
from app.presentation.graphql.permissions import IsAuthenticated
from app.presentation.graphql.products.mappers import to_product_type
from app.presentation.graphql.products.types import CreateProductInput, ProductType
from app.presentation.graphql.products.validators import CreateProductInputValidator
from app.presentation.graphql.validation import raise_graphql_validation_error


@strawberry.type
class ProductMutation:
    @strawberry.mutation(permission_classes=[IsAuthenticated])
    async def create_product(
        self,
        info: Info,
        input: CreateProductInput,
    ) -> ProductType:
        try:
            payload = CreateProductInputValidator.model_validate(
                {
                    "name": input.name,
                    "price": input.price,
                    "sku": input.sku,
                    "stock": input.stock,
                    "product_model_id": input.product_model_id,
                }
            )
        except ValidationError as exc:
            raise_graphql_validation_error(exc)

        container = get_container_from_context(info)
        product = await container.product_use_case.create_product(
            name=payload.name,
            price=payload.price,
            sku=payload.sku,
            stock=payload.stock,
            product_model_id=payload.product_model_id,
        )
        return to_product_type(product)
