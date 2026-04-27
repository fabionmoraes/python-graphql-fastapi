from sqlalchemy.orm import Session

from app.domain.entities.user import UserEntity
from app.domain.repositories.user_repository import UserRepository
from app.infrastructure.persistence.models.user_model import UserModel


class UserRepositoryImpl(UserRepository):
    def __init__(self, db: Session):
        self.db = db

    def list_users(self) -> list[UserEntity]:
        rows = self.db.query(UserModel).all()
        return [self._to_entity(row) for row in rows]

    def get_user_by_id(self, user_id: int) -> UserEntity | None:
        row = self.db.query(UserModel).filter(UserModel.id == user_id).first()
        if row is None:
            return None
        return self._to_entity(row)

    def get_user_by_credentials(self, username: str, email: str) -> UserEntity | None:
        row = (
            self.db.query(UserModel)
            .filter(UserModel.username == username, UserModel.email == email)
            .first()
        )
        if row is None:
            return None
        return self._to_entity(row)

    def create_user(
        self,
        username: str,
        email: str,
        role: str,
        is_active: bool,
    ) -> UserEntity:
        row = UserModel(
            username=username,
            email=email,
            role=role,
            is_active=is_active,
        )
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return self._to_entity(row)

    @staticmethod
    def _to_entity(row: UserModel) -> UserEntity:
        return UserEntity(
            id=row.id,
            username=row.username,
            email=row.email,
            role=row.role,
            is_active=row.is_active,
        )
