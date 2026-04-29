from app.application.dtos.user_dto import UserDTO
from app.core.security import hash_password
from app.domain.repositories.user_repository import UserRepository


class CreateUserUseCase:
    def __init__(self, repository: UserRepository) -> None:
        self.repository = repository

    async def execute(
        self,
        username: str,
        email: str,
        password: str,
        role: str = "USER",
        is_active: bool = True,
    ) -> UserDTO:
        user = await self.repository.create_user(
            username=username,
            email=email,
            password_hash=hash_password(password),
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
