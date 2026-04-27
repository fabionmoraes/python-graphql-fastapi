import strawberry
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.application.use_cases.create_user import CreateUserUseCase
from app.application.use_cases.login_user import LoginUserUseCase
from app.core.database import SessionLocal
from app.infrastructure.persistence.repositories.user_repository_impl import UserRepositoryImpl
from app.presentation.graphql.users.types import CreateUserInput, LoginInput, LoginResponseType, UserType
from app.presentation.graphql.users.validators import CreateUserInputValidator, LoginInputValidator
from app.presentation.graphql.validation import raise_graphql_validation_error


@strawberry.type
class UserMutation:
    @strawberry.mutation
    async def create_user(
        self,
        input: CreateUserInput,
    ) -> UserType:
        try:
            payload = CreateUserInputValidator.model_validate(
                {
                    "username": input.username,
                    "email": input.email,
                    "role": input.role,
                    "is_active": input.is_active,
                }
            )
        except ValidationError as exc:
            raise_graphql_validation_error(exc)

        db: Session = SessionLocal()
        try:
            repository = UserRepositoryImpl(db)
            use_case = CreateUserUseCase(repository)
            user = use_case.execute(
                username=payload.username,
                email=payload.email,
                role=payload.role,
                is_active=payload.is_active,
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
    async def login(self, input: LoginInput) -> LoginResponseType:
        try:
            payload = LoginInputValidator.model_validate(
                {
                    "username": input.username,
                    "email": input.email,
                }
            )
        except ValidationError as exc:
            raise_graphql_validation_error(exc)

        db: Session = SessionLocal()
        try:
            repository = UserRepositoryImpl(db)
            use_case = LoginUserUseCase(repository)
            result = use_case.execute(username=payload.username, email=payload.email)
            return LoginResponseType(
                access_token=result.access_token,
                token_type=result.token_type,
            )
        finally:
            db.close()
