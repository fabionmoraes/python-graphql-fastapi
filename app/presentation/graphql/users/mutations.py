import strawberry
from sqlalchemy.orm import Session

from app.application.use_cases.create_user import CreateUserUseCase
from app.application.use_cases.login_user import LoginUserUseCase
from app.core.database import SessionLocal
from app.infrastructure.persistence.repositories.user_repository_impl import UserRepositoryImpl
from app.presentation.graphql.users.types import LoginResponseType, UserType


@strawberry.type
class UserMutation:
    @strawberry.mutation
    def create_user(
        self,
        username: str,
        email: str,
        role: str = "USER",
        is_active: bool = True,
    ) -> UserType:
        db: Session = SessionLocal()
        try:
            repository = UserRepositoryImpl(db)
            use_case = CreateUserUseCase(repository)
            user = use_case.execute(
                username=username,
                email=email,
                role=role,
                is_active=is_active,
            )
            return UserType(
                id=user.id,
                username=user.username,
                email=user.email,
                role=user.role,
                is_active=user.is_active,
            )
        finally:
            db.close()

    @strawberry.mutation
    def login(self, username: str, email: str) -> LoginResponseType:
        db: Session = SessionLocal()
        try:
            repository = UserRepositoryImpl(db)
            use_case = LoginUserUseCase(repository)
            result = use_case.execute(username=username, email=email)
            return LoginResponseType(
                access_token=result.access_token,
                token_type=result.token_type,
            )
        finally:
            db.close()
