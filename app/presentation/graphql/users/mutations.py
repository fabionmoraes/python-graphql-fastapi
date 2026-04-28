import strawberry
from pydantic import ValidationError
from strawberry.types import Info

from app.application.use_cases.create_user import CreateUserUseCase
from app.application.use_cases.login_user import LoginUserUseCase
from app.infrastructure.persistence.repositories.user_repository_impl import (
    UserRepositoryImpl,
)
from app.presentation.graphql.context import get_db_from_context
from app.presentation.graphql.users.mappers import to_user_type
from app.presentation.graphql.users.types import (
    CreateUserInput,
    LoginInput,
    LoginResponseType,
    UserType,
)
from app.presentation.graphql.users.validators import (
    CreateUserInputValidator,
    LoginInputValidator,
)
from app.presentation.graphql.validation import raise_graphql_validation_error


@strawberry.type
class UserMutation:
    @strawberry.mutation
    def create_user(
        self,
        info: Info,
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

        db = get_db_from_context(info)
        repository = UserRepositoryImpl(db)
        use_case = CreateUserUseCase(repository)
        user = use_case.execute(
            username=payload.username,
            email=payload.email,
            role=payload.role,
            is_active=payload.is_active,
        )
        return to_user_type(user)

    @strawberry.mutation
    def login(self, info: Info, input: LoginInput) -> LoginResponseType:
        try:
            payload = LoginInputValidator.model_validate(
                {
                    "username": input.username,
                    "email": input.email,
                }
            )
        except ValidationError as exc:
            raise_graphql_validation_error(exc)

        db = get_db_from_context(info)
        repository = UserRepositoryImpl(db)
        use_case = LoginUserUseCase(repository)
        result = use_case.execute(username=payload.username, email=payload.email)
        return LoginResponseType(
            access_token=result.access_token,
            token_type=result.token_type,
        )
