from graphql import GraphQLError
from sqlalchemy.orm import Session
from strawberry.types import Info


def get_db_from_context(info: Info) -> Session:
    db = info.context.get("db")
    if db is None:
        raise GraphQLError("Database context not available.")
    return db
