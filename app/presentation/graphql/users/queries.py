import strawberry
from strawberry.types import Info

from app.application.use_cases.user_read_use_case import UserReadUseCase
from app.core.security import get_auth_from_header
from app.infrastructure.persistence.repositories.user_repository_impl import (
    UserRepositoryImpl,
)
from app.presentation.graphql.context import get_db_from_context
from app.presentation.graphql.users.mappers import to_user_type
from app.presentation.graphql.users.types import UserType


@strawberry.type
class UserQuery:
    @strawberry.field
    def users(self, info: Info) -> list[UserType]:
        get_auth_from_header(info)
        db = get_db_from_context(info)
        repository = UserRepositoryImpl(db)
        use_case = UserReadUseCase(repository)
        data = use_case.list_users()
        return [to_user_type(user) for user in data]

    @strawberry.field
    def user(self, info: Info, id: int) -> UserType | None:
        get_auth_from_header(info)
        db = get_db_from_context(info)
        repository = UserRepositoryImpl(db)
        use_case = UserReadUseCase(repository)
        user = use_case.get_user_by_id(id)
        if user is None:
            return None
        return to_user_type(user)
