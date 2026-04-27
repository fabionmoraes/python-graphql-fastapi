from graphql import GraphQLError

from app.application.dtos.user_dto import LoginResponseDTO
from app.core.security import create_access_token
from app.domain.repositories.user_repository import UserRepository


class LoginUserUseCase:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    def execute(self, username: str, email: str) -> LoginResponseDTO:
        user = self.repository.get_user_by_credentials(username=username, email=email)
        if user is None or not user.is_active:
            raise GraphQLError("Invalid credentials.")

        token = create_access_token(user_id=user.id, username=user.username)
        return LoginResponseDTO(access_token=token)
