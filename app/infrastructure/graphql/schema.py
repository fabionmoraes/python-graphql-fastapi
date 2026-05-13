import strawberry
from strawberry.extensions import DisableIntrospection, QueryDepthLimiter

from app.core.config import settings
from app.infrastructure.graphql.queries.catalog_query import CatalogQuery
from app.infrastructure.graphql.queries.product_query import ProductQuery


@strawberry.type
class Query(ProductQuery, CatalogQuery):
    pass


_extensions = [QueryDepthLimiter(max_depth=settings.GRAPHQL_MAX_QUERY_DEPTH)]

if settings.is_production:
    _extensions.append(DisableIntrospection())

schema = strawberry.Schema(
    query=Query,
    extensions=_extensions,
)
