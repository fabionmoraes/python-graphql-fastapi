import strawberry
from strawberry.types import Info

from app.presentation.graphql.context import get_container_from_context
from app.presentation.graphql.permissions import IsAuthenticated
from app.presentation.graphql.users.mappers import to_user_type
from app.presentation.graphql.users.types import UserType


@strawberry.type
class UserQuery:
    @strawberry.field(permission_classes=[IsAuthenticated])
    async def users(self, info: Info) -> list[UserType]:
        container = get_container_from_context(info)
        data = await container.user_read_use_case.list_users()
        return [to_user_type(user) for user in data]

    @strawberry.field(permission_classes=[IsAuthenticated])
    async def user(self, info: Info, id: int) -> UserType | None:
        container = get_container_from_context(info)
        user = await container.user_read_use_case.get_user_by_id(id)
        if user is None:
            return None
        return to_user_type(user)
