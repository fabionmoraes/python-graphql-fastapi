from abc import ABC, abstractmethod

from app.domain.entities.user import UserEntity


class UserRepository(ABC):
    @abstractmethod
    async def list_users(self) -> list[UserEntity]:
        raise NotImplementedError

    @abstractmethod
    async def get_user_by_id(self, user_id: int) -> UserEntity | None:
        raise NotImplementedError

    @abstractmethod
    async def get_user_by_email(self, email: str) -> UserEntity | None:
        raise NotImplementedError

    @abstractmethod
    async def create_user(
        self,
        username: str,
        email: str,
        password_hash: str,
        role: str,
        is_active: bool,
    ) -> UserEntity:
        raise NotImplementedError
