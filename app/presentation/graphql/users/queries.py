import strawberry
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.infrastructure.persistence.repositories.user_repository_impl import UserRepositoryImpl
from app.presentation.graphql.users.types import UserType


@strawberry.type
class UserQuery:
    @strawberry.field
    def users(self) -> list[UserType]:
        db: Session = SessionLocal()
        try:
            repository = UserRepositoryImpl(db)
            data = repository.list_users()
            return [
                UserType(
                    id=user.id,
                    username=user.username,
                    email=user.email,
                    role=user.role,
                    is_active=user.is_active,
                )
                for user in data
            ]
        finally:
            db.close()

    @strawberry.field
    def user(self, id: int) -> UserType | None:
        db: Session = SessionLocal()
        try:
            repository = UserRepositoryImpl(db)
            user = repository.get_user_by_id(id)
            if user is None:
                return None
            return UserType(
                id=user.id,
                username=user.username,
                email=user.email,
                role=user.role,
                is_active=user.is_active,
            )
        finally:
            db.close()
