from graphql import GraphQLError
from sqlalchemy.orm import Session
from strawberry.dataloader import DataLoader
from strawberry.types import Info

from app.core.container import Container
from app.domain.entities.product import ProductEntity


def get_db_from_context(info: Info) -> Session:
    db = info.context.get("db")
    if db is None:
        raise GraphQLError("Database context not available.")
    return db


def get_container_from_context(info: Info) -> Container:
    container = info.context.get("container")
    if container is None:
        raise GraphQLError("Container context not available.")
    return container


def get_product_loader_from_context(info: Info) -> DataLoader[int, ProductEntity | None]:
    loader = info.context.get("product_by_id_loader")
    if loader is None:
        raise GraphQLError("Product DataLoader context not available.")
    return loader
