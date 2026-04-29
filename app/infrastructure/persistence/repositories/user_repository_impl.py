from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.user import UserEntity
from app.domain.repositories.user_repository import UserRepository
from app.infrastructure.persistence.models.user_model import UserModel


class UserRepositoryImpl(UserRepository):
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def list_users(self) -> list[UserEntity]:
        result = await self.db.execute(select(UserModel))
        rows = result.scalars().all()
        return [self._to_entity(row) for row in rows]

    async def get_user_by_id(self, user_id: int) -> UserEntity | None:
        result = await self.db.execute(
            select(UserModel).where(UserModel.id == user_id)
        )
        row = result.scalars().first()
        if row is None:
            return None
        return self._to_entity(row)

    async def get_user_by_email(self, email: str) -> UserEntity | None:
        result = await self.db.execute(
            select(UserModel).where(UserModel.email == email)
        )
        row = result.scalars().first()
        if row is None:
            return None
        return self._to_entity(row)

    async def create_user(
        self,
        username: str,
        email: str,
        password_hash: str,
        role: str,
        is_active: bool,
    ) -> UserEntity:
        row = UserModel(
            username=username,
            email=email,
            password_hash=password_hash,
            role=role,
            is_active=is_active,
        )
        self.db.add(row)
        await self.db.commit()
        await self.db.refresh(row)
        return self._to_entity(row)

    @staticmethod
    def _to_entity(row: UserModel) -> UserEntity:
        return UserEntity(
            id=row.id,
            username=row.username,
            email=row.email,
            password_hash=row.password_hash,
            role=row.role,
            is_active=row.is_active,
        )
