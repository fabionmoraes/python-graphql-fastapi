from functools import cached_property

from sqlalchemy.ext.asyncio import AsyncSession

from app.application.use_cases.create_user import CreateUserUseCase
from app.application.use_cases.login_user import LoginUserUseCase
from app.application.use_cases.order_use_case import OrderUseCase
from app.application.use_cases.product_use_case import ProductUseCase
from app.application.use_cases.user_read_use_case import UserReadUseCase
from app.infrastructure.persistence.repositories.order_repository_impl import (
    OrderRepositoryImpl,
)
from app.infrastructure.persistence.repositories.product_repository_impl import (
    ProductRepositoryImpl,
)
from app.infrastructure.persistence.repositories.user_repository_impl import (
    UserRepositoryImpl,
)


class Container:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    @cached_property
    def order_use_case(self) -> OrderUseCase:
        return OrderUseCase(OrderRepositoryImpl(self.db))

    @cached_property
    def product_use_case(self) -> ProductUseCase:
        return ProductUseCase(ProductRepositoryImpl(self.db))

    @cached_property
    def user_read_use_case(self) -> UserReadUseCase:
        return UserReadUseCase(UserRepositoryImpl(self.db))

    @cached_property
    def create_user_use_case(self) -> CreateUserUseCase:
        return CreateUserUseCase(UserRepositoryImpl(self.db))

    @cached_property
    def login_user_use_case(self) -> LoginUserUseCase:
        return LoginUserUseCase(UserRepositoryImpl(self.db))
