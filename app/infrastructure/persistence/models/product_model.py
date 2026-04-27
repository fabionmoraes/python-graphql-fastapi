from sqlalchemy import Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class ProductCatalogModel(Base):
    __tablename__ = "product_model"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String, nullable=False)


class ProductModel(Base):
    __tablename__ = "items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    sku: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    stock: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    product_model_id: Mapped[int | None] = mapped_column(
        ForeignKey("product_model.id"),
        nullable=True,
    )
    product_model: Mapped[ProductCatalogModel | None] = relationship()
