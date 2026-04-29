from graphql import GraphQLError

from app.domain.entities.pagination import PageResult
from app.domain.entities.user import UserEntity
from app.domain.repositories.user_repository import UserRepository

_MAX_FIRST = 100


class UserReadUseCase:
    def __init__(self, repository: UserRepository) -> None:
        self.repository = repository

    async def list_users(self) -> list[UserEntity]:
        return await self.repository.list_users()

    async def list_users_paginated(
        self, first: int, after_id: int | None
    ) -> PageResult[UserEntity]:
        if first < 1 or first > _MAX_FIRST:
            raise GraphQLError(f"'first' must be between 1 and {_MAX_FIRST}.")
        return await self.repository.list_users_paginated(first=first, after_id=after_id)

    async def get_user_by_id(self, user_id: int) -> UserEntity | None:
        return await self.repository.get_user_by_id(user_id=user_id)
