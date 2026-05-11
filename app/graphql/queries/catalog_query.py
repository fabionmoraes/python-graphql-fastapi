import strawberry
from graphql import GraphQLError
from strawberry.types import Info

from app.graphql.context import get_container_from_context
from app.graphql.pagination import Connection, build_connection, decode_cursor
from app.graphql.types.mappers import to_catalog_type
from app.graphql.types.product_type import ProductCatalogType
from app.graphql.utils.selection import parse_selected_fields
from app.graphql.utils.constants import MAX_FIRST


@strawberry.type
class CatalogQuery:
    @strawberry.field
    async def product_catalogs(
        self,
        info: Info,
        first: int = 20,
        after: str | None = None,
    ) -> Connection[ProductCatalogType]:
        if first < 1 or first > MAX_FIRST:
            raise GraphQLError(f"'first' must be between 1 and {MAX_FIRST}.")

        container = get_container_from_context(info)
        all_fields = parse_selected_fields(info)
        node_fields = all_fields.get("edges", {}).get("node", {})
        need_total = "totalCount" in all_fields
        after_id = decode_cursor(after) if after else None

        page = await container.catalog_service.list_catalogs(
            selected_fields=node_fields,
            first=first,
            after_id=after_id,
            need_total=need_total,
        )
        return build_connection(page, to_catalog_type, lambda c: c.id)

    @strawberry.field
    async def product_catalog(
        self, info: Info, id: int
    ) -> ProductCatalogType | None:
        container = get_container_from_context(info)
        selected_fields = parse_selected_fields(info)
        catalog = await container.catalog_service.get_catalog(id, selected_fields)
        if catalog is None:
            return None
        return to_catalog_type(catalog)
