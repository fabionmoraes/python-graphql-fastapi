import base64
from collections.abc import Callable
from typing import Generic, TypeVar

import strawberry
from graphql import GraphQLError

from app.domain.entities.pagination import PageResult

T = TypeVar("T")
E = TypeVar("E")


def encode_cursor(id: int) -> str:
    return base64.b64encode(f"cursor:{id}".encode()).decode()


def decode_cursor(cursor: str) -> int:
    try:
        decoded = base64.b64decode(cursor.encode()).decode()
        _, id_str = decoded.split(":", 1)
        return int(id_str)
    except Exception as exc:
        raise GraphQLError(f"Invalid cursor: {cursor!r}") from exc


@strawberry.type
class PageInfo:
    has_next_page: bool
    has_previous_page: bool
    start_cursor: str | None
    end_cursor: str | None


@strawberry.type
class Edge(Generic[T]):
    cursor: str
    node: T


@strawberry.type
class Connection(Generic[T]):
    edges: list[Edge[T]]
    page_info: PageInfo
    total_count: int


def build_connection(
    page: PageResult[E],
    to_type: Callable[[E], T],
    get_id: Callable[[E], int],
) -> Connection[T]:
    edges = [
        Edge(cursor=encode_cursor(get_id(item)), node=to_type(item))
        for item in page.items
    ]
    start = edges[0].cursor if edges else None
    end = edges[-1].cursor if edges else None
    return Connection(
        edges=edges,
        page_info=PageInfo(
            has_next_page=page.has_next_page,
            has_previous_page=page.has_previous_page,
            start_cursor=start,
            end_cursor=end,
        ),
        total_count=page.total_count,
    )
