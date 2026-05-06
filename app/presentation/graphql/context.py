from graphql import GraphQLError
from strawberry.types import Info

from app.core.container import Container


def get_container_from_context(info: Info) -> Container:
    container = info.context.get("container")
    if container is None:
        raise GraphQLError("Container context not available.")
    return container
