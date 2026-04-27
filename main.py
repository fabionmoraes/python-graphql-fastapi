from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter

from app.core.database import Base, engine
from app.infrastructure.persistence.models.order_model import OrderModel
from app.infrastructure.persistence.models.product_model import ProductModel
from app.infrastructure.persistence.models.user_model import UserModel
from app.presentation.graphql.schema import schema

# Keep compatibility with current execution command: uvicorn main:app --reload
_ = (UserModel, ProductModel, OrderModel)
app = FastAPI(title="GraphQL Python + FastAPI + SQLAlchemy + JWT")
Base.metadata.create_all(bind=engine)
app.include_router(GraphQLRouter(schema), prefix="/graphql")