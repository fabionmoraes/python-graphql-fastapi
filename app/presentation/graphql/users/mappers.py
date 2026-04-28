from app.domain.entities.user import UserEntity
from app.presentation.graphql.users.types import UserType


def to_user_type(user: UserEntity) -> UserType:
    return UserType(
        id=user.id,
        username=user.username,
        email=user.email,
        role=user.role,
        is_active=user.is_active,
    )
