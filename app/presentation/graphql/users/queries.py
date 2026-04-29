import strawberry
from strawberry.types import Info

from app.presentation.graphql.context import get_container_from_context
from app.presentation.graphql.pagination import (
    Connection,
    build_connection,
    decode_cursor,
)
from app.presentation.graphql.permissions import IsAuthenticated
from app.presentation.graphql.users.mappers import to_user_type
from app.presentation.graphql.users.types import UserType


@strawberry.type
class UserQuery:
    @strawberry.field(permission_classes=[IsAuthenticated])
    async def users(
        self,
        info: Info,
        first: int = 20,
        after: str | None = None,
    ) -> Connection[UserType]:
        container = get_container_from_context(info)
        after_id = decode_cursor(after) if after else None
        page = await container.user_read_use_case.list_users_paginated(
            first=first, after_id=after_id
        )
        return build_connection(page, to_user_type, lambda u: u.id)

    @strawberry.field(permission_classes=[IsAuthenticated])
    async def user(self, info: Info, id: int) -> UserType | None:
        container = get_container_from_context(info)
        user = await container.user_read_use_case.get_user_by_id(id)
        if user is None:
            return None
        return to_user_type(user)
