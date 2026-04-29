from graphql import GraphQLError

from app.application.dtos.user_dto import LoginResponseDTO
from app.core.security import create_access_token, verify_password
from app.domain.repositories.user_repository import UserRepository


class LoginUserUseCase:
    def __init__(self, repository: UserRepository) -> None:
        self.repository = repository

    async def execute(self, email: str, password: str) -> LoginResponseDTO:
        user = await self.repository.get_user_by_email(email=email)
        if user is None or not user.is_active:
            raise GraphQLError("Invalid credentials.")
        if not verify_password(password=password, encoded_password=user.password_hash):
            raise GraphQLError("Invalid credentials.")

        token = create_access_token(user_id=user.id, username=user.username)
        return LoginResponseDTO(access_token=token)
