from app.application.dtos.user_dto import UserDTO
from app.domain.repositories.user_repository import UserRepository


class CreateUserUseCase:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    def execute(
        self,
        username: str,
        email: str,
        role: str = "USER",
        is_active: bool = True,
    ) -> UserDTO:
        user = self.repository.create_user(
            username=username,
            email=email,
            role=role,
            is_active=is_active,
        )
        return UserDTO(
            id=user.id,
            username=user.username,
            email=user.email,
            role=user.role,
            is_active=user.is_active,
        )
