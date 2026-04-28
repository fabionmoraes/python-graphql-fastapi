from app.domain.entities.user import UserEntity
from app.domain.repositories.user_repository import UserRepository


class UserReadUseCase:
    def __init__(self, repository: UserRepository) -> None:
        self.repository = repository

    def list_users(self) -> list[UserEntity]:
        return self.repository.list_users()

    def get_user_by_id(self, user_id: int) -> UserEntity | None:
        return self.repository.get_user_by_id(user_id=user_id)
