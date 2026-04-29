from graphql import GraphQLError
from sqlalchemy.ext.asyncio import AsyncSession
from strawberry.types import Info

from app.core.container import Container
from app.presentation.graphql.loaders import Loaders


def get_db_from_context(info: Info) -> AsyncSession:
    db = info.context.get("db")
    if db is None:
        raise GraphQLError("Database context not available.")
    return db


def get_container_from_context(info: Info) -> Container:
    container = info.context.get("container")
    if container is None:
        raise GraphQLError("Container context not available.")
    return container


def get_loaders_from_context(info: Info) -> Loaders:
    loaders = info.context.get("loaders")
    if loaders is None:
        raise GraphQLError("Loaders context not available.")
    return loaders
