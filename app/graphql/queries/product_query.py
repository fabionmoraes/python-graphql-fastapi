import strawberry
from graphql import GraphQLError
from strawberry.types import Info

from app.domain.entities.product import ProductWhereEntity, StringComparisonEntity
from app.graphql.context import get_container_from_context
from app.graphql.pagination import Connection, build_connection, decode_cursor
from app.graphql.types.mappers import to_product_type
from app.graphql.types.product_type import ProductType, ProductWhereInput, StringComparisonExp
from app.graphql.utils.selection import parse_selected_fields

_MAX_FIRST = 100


def _to_string_comparison(exp: StringComparisonExp | None) -> StringComparisonEntity | None:
    if exp is None:
        return None
    return StringComparisonEntity(eq=exp._eq, like=exp._like, one_of=exp._in)


def _to_where_entity(where: ProductWhereInput | None) -> ProductWhereEntity | None:
    if where is None:
        return None
    return ProductWhereEntity(
        name=_to_string_comparison(where.name),
        sku=_to_string_comparison(where.sku),
        model_title=_to_string_comparison(where.model_title),
    )


@strawberry.type
class ProductQuery:
    @strawberry.field
    async def products(
        self,
        info: Info,
        first: int = 20,
        after: str | None = None,
        where: ProductWhereInput | None = None,
    ) -> Connection[ProductType]:
        if first < 1 or first > _MAX_FIRST:
            raise GraphQLError(f"'first' must be between 1 and {_MAX_FIRST}.")

        container = get_container_from_context(info)
        all_fields = parse_selected_fields(info)
        node_fields = all_fields.get("edges", {}).get("node", {})
        need_total = "totalCount" in all_fields
        after_id = decode_cursor(after) if after else None

        page = await container.product_service.list_products(
            selected_fields=node_fields,
            first=first,
            after_id=after_id,
            where=_to_where_entity(where),
            need_total=need_total,
        )
        return build_connection(page, to_product_type, lambda p: p.id)

    @strawberry.field
    async def product(self, info: Info, id: int) -> ProductType | None:
        container = get_container_from_context(info)
        selected_fields = parse_selected_fields(info)
        product = await container.product_service.get_product(id, selected_fields)
        if product is None:
            return None
        return to_product_type(product)
