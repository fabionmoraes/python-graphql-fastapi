import strawberry


@strawberry.type
class UserType:
    id: int
    username: str
    email: str
    role: str
    is_active: bool


@strawberry.type
class LoginResponseType:
    access_token: str
    token_type: str = "Bearer"


@strawberry.input
class CreateUserInput:
    username: str
    email: str
    role: str = "USER"
    is_active: bool = True


@strawberry.input
class LoginInput:
    username: str
    email: str
